#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KanjiVG のストローク点列を COBOTTA の絶対 P 座標へ変換して書字する。

このモジュールは、一行分の文字列をレイアウトした結果から筆画を取り出し、
COBOTTA に対して直線補間の絶対位置指令を送る。書字開始時のロボット姿勢を
作業空間の原点として保持し、文字座標からロボット座標への変換を一貫して行う。

書字動作は、筆画内の描画と筆画間の空走を明確に分離する。筆画内ではペン先の
Z 座標を書字面に固定し、各点を非同期の NEXT 指定で連続投入する。筆画間では、
直前の終点でペンを上げ、次の始点まで移動してからペンを下ろす。この構成により、
一つの筆画中に不要なペンの上下動作を挿入しない。

Notes:
    - :meth:`FontBcapCobottaWriter.write` は一行だけを処理する。
    - 作業空間および文字セルの大きさは設定値として固定する。
    - ロボットへの目標値はすべて絶対 P 座標で与える。
    - 相対移動用の ``robo_dmove_P()`` は使用しない。
    - 書字面の高さは、``write()`` 呼び出し時の開始姿勢と
      ``start_height_mm`` から決定する。
"""

import logging
from pathlib import Path
from typing import Any, List, Optional, Sequence

from cobotta2.cobotta_bcap import CobottaBcap
from glyph_motion.font_line_layout import FontLineLayout
from glyph_motion.font_line_layout import PositionedCharacter
from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokePath


class FontBcapCobottaWriterConfig:
    """一行書字に使用する設定値を保持する。

    通信先、文字レイアウト、座標変換、速度および加減速の設定を一つにまとめる。
    このクラスは値の保持と基本的な型変換だけを担当し、設定値の妥当性検証や
    ロボットへの反映は :class:`FontBcapCobottaWriter` が行う。

    Args:
        kanjivg_directory: KanjiVG データを格納したディレクトリ。
        host: COBOTTA コントローラのホスト名または IP アドレス。
        port: b-CAP 接続に使用するポート番号。
        workspace_width: 一行を書き込む作業空間の幅 [mm]。
        workspace_height: 一行を書き込む作業空間の高さ [mm]。
        cell_width: 一文字分のセル幅 [mm]。
        cell_height: 一文字分のセル高さ [mm]。
        character_height: セル内に配置する文字の高さ [mm]。
        curve_division: ベジェ曲線を点列へ展開する際の分割数。
        pen_lift_mm: 書字面からペンを退避させる高さ [mm]。
        robot_x_sign: 文字座標の X 成分に適用する符号。
        robot_y_sign: 文字座標の Y 成分に適用する符号。
        robot_swap_xy: 文字座標の X 軸と Y 軸を交換するか。
        line_direction: 横書き時に文字を並べる方向。
        writing_direction: 横書きまたは縦書きの指定。
        vertical_direction: 縦書き時に文字を並べる方向。
        horizontal_new_line_direction: 横書き時に次の行へ送る方向。
        vertical_new_line_direction: 縦書き時に次の列へ送る方向。
        mirror_horizontal: 文字を左右反転するか。
        mirror_vertical: 文字を上下反転するか。
        drawing_speed: 筆画を描画する際の速度設定。
        travel_speed: ペンを上げた状態で移動する際の速度設定。
        pen_speed: ペンを上下させる際の速度設定。
        accel: ロボットへ設定する加速度。
        decel: ロボットへ設定する減速度。
    """

    def __init__(
        self,
        kanjivg_directory,
        host="10.170.10.53",
        port=5007,
        # 書字ワークスペースの大きさ
        workspace_width=200.0,
        workspace_height=10.0,
        # 一文字の箱の大きさ
        cell_width=8.0,
        cell_height=8.0,
        # 箱の中の文字の高さ
        character_height=7.0,
        # ---- ベジェ曲線の分割数
        curve_division=16,
        # ペン上げ高さ [mm]
        pen_lift_mm=1.0,
        # ロボット座標系の方向
        robot_x_sign=1.0,
        robot_y_sign=1.0,
        robot_swap_xy=False,
        # 文字を配置する順序
        line_direction="left_to_right",
        # 横書き・縦書き
        writing_direction="horizontal",
        # 縦書き時の進行方向
        vertical_direction="top_to_bottom",
        # 横書き時の改行方向
        horizontal_new_line_direction="top_to_bottom",
        # 縦書き時の改列方向
        vertical_new_line_direction="right_to_left",
        # 文字の左右反転
        mirror_horizontal=False,
        # 文字の上下反転
        mirror_vertical=False,
        # 書字速度
        drawing_speed=35,
        # 空走速度
        travel_speed=40,
        # ペン上下速度
        pen_speed=20,
        accel=100,
        decel=100,
    ):
        self.kanjivg_directory = kanjivg_directory
        self.host = host
        self.port = int(port)
        self.workspace_width = float(workspace_width)
        self.workspace_height = float(workspace_height)
        self.cell_width = float(cell_width)
        self.cell_height = float(cell_height)
        self.character_height = float(character_height)
        self.curve_division = int(curve_division)
        self.pen_lift_mm = float(pen_lift_mm)
        self.robot_x_sign = float(robot_x_sign)
        self.robot_y_sign = float(robot_y_sign)
        self.robot_swap_xy = bool(robot_swap_xy)
        self.line_direction = str(line_direction)
        self.writing_direction = str(writing_direction)
        self.vertical_direction = str(vertical_direction)
        self.horizontal_new_line_direction = str(horizontal_new_line_direction)
        self.vertical_new_line_direction = str(vertical_new_line_direction)

        if self.horizontal_new_line_direction not in (
            "top_to_bottom",
            "bottom_to_top",
        ):
            raise ValueError(
                "horizontal_new_line_direction は "
                "top_to_bottom または bottom_to_top を指定してください。"
            )

        if self.vertical_new_line_direction not in (
            "left_to_right",
            "right_to_left",
        ):
            raise ValueError(
                "vertical_new_line_direction は "
                "left_to_right または right_to_left を指定してください。"
            )

        self.mirror_horizontal = bool(mirror_horizontal)
        self.mirror_vertical = bool(mirror_vertical)
        self.drawing_speed = int(drawing_speed)
        self.travel_speed = int(travel_speed)
        self.pen_speed = int(pen_speed)
        self.accel = int(accel)
        self.decel = int(decel)


class FontBcapCobottaWriter:
    """固定作業空間へ一行の文字列を書く。

    書字開始時の現在姿勢を作業空間の基準姿勢として使用する。文字レイアウトから
    得られる二次元点列をロボットの絶対 P 座標へ変換し、ペンの上下、筆画間の空走、
    筆画内の連続描画を順番に実行する。

    Args:
        config: 書字条件を保持する設定オブジェクト。
        bcap: 既存の :class:`CobottaBcap` インスタンス。省略した場合は本クラスが
            接続用インスタンスを生成し、終了時に切断する。
        logger: ログ出力に使用する logger。省略時はモジュール logger を生成する。

    Attributes:
        config: 現在の書字設定。
    """

    def __init__(
        self,
        config,
        bcap=None,
        logger=None,
    ):
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

        self.config = config
        self._logger = logger
        self._bcap = bcap
        self._owns_bcap = bcap is None
        self._connected = False
        self._arm_taken = False
        self._write_in_progress = False
        self._emergency_pen_up_z = None
        self._document_origin = None
        self._document_surface_z = None
        self._cursor_x = 0.0
        self._cursor_y = 0.0
        self._has_written = False
        self._start_height_mm = 0.0
        self._return_to_start = True
        self._new_line = False

        self._layout = FontLineLayout(
            kanjivg_directory=config.kanjivg_directory,
            workspace_width=config.workspace_width,
            workspace_height=config.workspace_height,
            cell_width=config.cell_width,
            cell_height=config.cell_height,
            character_height=config.character_height,
            curve_division=config.curve_division,
            line_direction=config.line_direction,
            writing_direction=config.writing_direction,
            vertical_direction=config.vertical_direction,
            mirror_horizontal=config.mirror_horizontal,
            mirror_vertical=config.mirror_vertical,
        )

    def connect(self):
        """COBOTTA との b-CAP 接続を確立する。

        既に接続済みの場合は再接続を行わない。外部から ``bcap`` が渡されていない
        場合に限り、設定されたホストとポートを用いて接続インスタンスを生成する。

        Returns:
            接続済み、または接続に成功した場合は ``True``。接続に失敗した場合は
            ``False``。
        """
        if self._connected:
            return True

        if self._bcap is None:
            self._bcap = CobottaBcap(
                host=self.config.host,
                port=self.config.port,
                logger=self._logger,
            )

        if not self._bcap.connect():
            return False

        self._connected = True
        return True

    def disconnect(self):
        """COBOTTA との b-CAP 接続を切断する。

        他のロボット操作は行わず、通信接続だけを切断する。

        Returns:
            切断に成功した場合は ``True``。未接続の場合も ``True``。
        """
        if self._bcap is None or not self._connected:
            return True

        result = self._bcap.disconnect()
        if result is False:
            return False

        self._connected = False
        self._document_origin = None
        self._document_surface_z = None
        self._cursor_x = 0.0
        self._cursor_y = 0.0
        self._has_written = False
        return True

    def reset_error(self):
        """コントローラのエラーを解除する。

        Returns:
            エラー解除に成功した場合は ``True``、失敗した場合は ``False``。
        """
        if not self._connected or self._bcap is None:
            return False
        return self._bcap.reset_error()

    def take_arm(self):
        """アーム権限を取得する。

        他の準備処理は行わず、TakeArm だけを実行する。

        Returns:
            アーム権限の取得に成功した場合は ``True``、失敗した場合は ``False``。
        """
        if not self._connected or self._bcap is None:
            return False

        if not self._bcap.take_arm():
            return False

        self._arm_taken = True
        return True

    def give_arm(self):
        """取得済みのアーム権限を返却する。

        緊急退避や切断などの別操作は行わず、GiveArm だけを実行する。

        Returns:
            アーム権限の返却に成功した場合は ``True``。未取得の場合も ``True``。
        """
        if not self._arm_taken:
            return True
        if self._bcap is None:
            return False

        if not self._bcap.give_arm():
            return False

        self._arm_taken = False
        return True

    def motor_on(self):
        """ロボットのモータを投入する。

        Returns:
            モータ投入に成功した場合は ``True``、失敗した場合は ``False``。
        """
        if not self._connected or self._bcap is None:
            return False
        return self._bcap.motor_on()

    def set_accel(self):
        """設定済みの加速度をロボットへ反映する。

        Returns:
            加速度設定に成功した場合は ``True``、失敗した場合は ``False``。
        """
        if not self._connected or self._bcap is None:
            return False
        return self._bcap.set_accel(self.config.accel)

    def set_decel(self):
        """設定済みの減速度をロボットへ反映する。

        Returns:
            減速度設定に成功した場合は ``True``、失敗した場合は ``False``。
        """
        if not self._connected or self._bcap is None:
            return False
        return self._bcap.set_decel(self.config.decel)

    def set_params(
        self,
        kanjivg_directory: Optional[Path] = None,
        workspace_width: Optional[float] = None,
        workspace_height: Optional[float] = None,
        cell_width: Optional[float] = None,
        cell_height: Optional[float] = None,
        character_height: Optional[float] = None,
        curve_division: Optional[int] = None,
        pen_lift_mm: Optional[float] = None,
        robot_x_sign: Optional[float] = None,
        robot_y_sign: Optional[float] = None,
        robot_swap_xy: Optional[bool] = None,
        line_direction: Optional[str] = None,
        writing_direction: Optional[str] = None,
        vertical_direction: Optional[str] = None,
        horizontal_new_line_direction: Optional[str] = None,
        vertical_new_line_direction: Optional[str] = None,
        mirror_horizontal: Optional[bool] = None,
        mirror_vertical: Optional[bool] = None,
        drawing_speed: Optional[int] = None,
        travel_speed: Optional[int] = None,
        pen_speed: Optional[int] = None,
        accel: Optional[int] = None,
        decel: Optional[int] = None,
    ) -> bool:
        """通信設定以外の書字設定を更新する。

        ``None`` が指定された項目は現在値を維持する。文字配置に影響する設定は、
        まず新しい値をローカル変数へ集約し、その値から新しい
        :class:`FontLineLayout` を構築した後で設定へ反映する。これにより、
        レイアウト生成に失敗した状態で既存設定だけが部分的に更新されることを防ぐ。

        Args:
            kanjivg_directory: 新しい KanjiVG ディレクトリ。
            workspace_width: 新しい作業空間幅 [mm]。
            workspace_height: 新しい作業空間高さ [mm]。
            cell_width: 新しい文字セル幅 [mm]。
            cell_height: 新しい文字セル高さ [mm]。
            character_height: 新しい文字高さ [mm]。
            curve_division: 新しいベジェ曲線分割数。
            pen_lift_mm: 新しいペン退避高さ [mm]。
            robot_x_sign: 文字 X 座標へ適用する新しい符号。
            robot_y_sign: 文字 Y 座標へ適用する新しい符号。
            robot_swap_xy: 文字座標の X 軸と Y 軸を交換するか。
            line_direction: 横書き時の新しい進行方向。
            writing_direction: 新しい書字方向。
            vertical_direction: 縦書き時の新しい進行方向。
            horizontal_new_line_direction: 横書き時の新しい改行方向。
            vertical_new_line_direction: 縦書き時の新しい改列方向。
            mirror_horizontal: 左右反転を有効にするか。
            mirror_vertical: 上下反転を有効にするか。
            drawing_speed: 新しい描画速度。
            travel_speed: 新しい空走速度。
            pen_speed: 新しいペン上下速度。
            accel: 新しい加速度。
            decel: 新しい減速度。

        Returns:
            設定更新に成功した場合は ``True``。
        """
        # レイアウト生成に関係する変更と、ロボット動作だけに関係する変更を分けて扱う。
        layout_changed = False

        new_kanjivg_directory = self.config.kanjivg_directory
        new_workspace_width = self.config.workspace_width
        new_workspace_height = self.config.workspace_height
        new_cell_width = self.config.cell_width
        new_cell_height = self.config.cell_height
        new_character_height = self.config.character_height
        new_curve_division = self.config.curve_division
        new_line_direction = self.config.line_direction
        new_writing_direction = self.config.writing_direction
        new_vertical_direction = self.config.vertical_direction
        new_horizontal_new_line_direction = (
            self.config.horizontal_new_line_direction
        )
        new_vertical_new_line_direction = self.config.vertical_new_line_direction
        new_mirror_horizontal = self.config.mirror_horizontal
        new_mirror_vertical = self.config.mirror_vertical

        if kanjivg_directory is not None:
            new_kanjivg_directory = Path(kanjivg_directory)
            layout_changed = True

        if workspace_width is not None:
            new_workspace_width = float(workspace_width)
            layout_changed = True

        if workspace_height is not None:
            new_workspace_height = float(workspace_height)
            layout_changed = True

        if cell_width is not None:
            new_cell_width = float(cell_width)
            layout_changed = True

        if cell_height is not None:
            new_cell_height = float(cell_height)
            layout_changed = True

        if character_height is not None:
            new_character_height = float(character_height)
            layout_changed = True

        if curve_division is not None:
            new_curve_division = int(curve_division)
            layout_changed = True

        if line_direction is not None:
            new_line_direction = str(line_direction)
            layout_changed = True

        if writing_direction is not None:
            new_writing_direction = str(writing_direction)
            layout_changed = True

        if vertical_direction is not None:
            new_vertical_direction = str(vertical_direction)
            layout_changed = True

        if horizontal_new_line_direction is not None:
            new_horizontal_new_line_direction = str(
                horizontal_new_line_direction
            )
            if new_horizontal_new_line_direction not in (
                "top_to_bottom",
                "bottom_to_top",
            ):
                raise ValueError(
                    "horizontal_new_line_direction は "
                    "top_to_bottom または bottom_to_top を指定してください。"
                )

        if vertical_new_line_direction is not None:
            new_vertical_new_line_direction = str(vertical_new_line_direction)
            if new_vertical_new_line_direction not in (
                "left_to_right",
                "right_to_left",
            ):
                raise ValueError(
                    "vertical_new_line_direction は "
                    "left_to_right または right_to_left を指定してください。"
                )

        if mirror_horizontal is not None:
            new_mirror_horizontal = bool(mirror_horizontal)
            layout_changed = True

        if mirror_vertical is not None:
            new_mirror_vertical = bool(mirror_vertical)
            layout_changed = True

        # 新しいレイアウトは設定値を書き換える前に生成する。生成失敗時は旧設定を保つ。
        new_layout = None
        if layout_changed:
            new_layout = FontLineLayout(
                kanjivg_directory=new_kanjivg_directory,
                workspace_width=new_workspace_width,
                workspace_height=new_workspace_height,
                cell_width=new_cell_width,
                cell_height=new_cell_height,
                character_height=new_character_height,
                curve_division=new_curve_division,
                line_direction=new_line_direction,
                writing_direction=new_writing_direction,
                vertical_direction=new_vertical_direction,
                mirror_horizontal=new_mirror_horizontal,
                mirror_vertical=new_mirror_vertical,
            )

        self.config.kanjivg_directory = new_kanjivg_directory
        self.config.workspace_width = new_workspace_width
        self.config.workspace_height = new_workspace_height
        self.config.cell_width = new_cell_width
        self.config.cell_height = new_cell_height
        self.config.character_height = new_character_height
        self.config.curve_division = new_curve_division
        self.config.line_direction = new_line_direction
        self.config.writing_direction = new_writing_direction
        self.config.vertical_direction = new_vertical_direction
        self.config.horizontal_new_line_direction = (
            new_horizontal_new_line_direction
        )
        self.config.vertical_new_line_direction = new_vertical_new_line_direction
        self.config.mirror_horizontal = new_mirror_horizontal
        self.config.mirror_vertical = new_mirror_vertical

        if pen_lift_mm is not None:
            self.config.pen_lift_mm = float(pen_lift_mm)

        if robot_x_sign is not None:
            self.config.robot_x_sign = float(robot_x_sign)

        if robot_y_sign is not None:
            self.config.robot_y_sign = float(robot_y_sign)

        if robot_swap_xy is not None:
            self.config.robot_swap_xy = bool(robot_swap_xy)

        if drawing_speed is not None:
            self.config.drawing_speed = int(drawing_speed)

        if travel_speed is not None:
            self.config.travel_speed = int(travel_speed)

        if pen_speed is not None:
            self.config.pen_speed = int(pen_speed)

        if accel is not None:
            self.config.accel = int(accel)

        if decel is not None:
            self.config.decel = int(decel)

        if new_layout is not None:
            self._layout = new_layout

        return True

    def set_pen_lift_mm(self, pen_lift_mm: float) -> bool:
        """書字面からのペン退避高さを設定する。

        Args:
            pen_lift_mm: 筆画間および書字終了時のペン上げ高さ [mm]。
                文字列として渡された数値も受け付ける。

        Returns:
            設定に成功した場合は ``True``。

        Raises:
            ValueError: ``pen_lift_mm`` が負の場合。
        """
        pen_lift_mm = float(pen_lift_mm)
        if pen_lift_mm < 0.0:
            raise ValueError("pen_lift_mm は 0.0 以上で指定してください。")

        self.config.pen_lift_mm = pen_lift_mm
        return True

    def set_start_height_mm(self, start_height_mm: float) -> bool:
        """``write()`` の既定の書字開始高さを設定する。

        Args:
            start_height_mm: 書字開始位置が書字面より高い量 [mm]。
                文字列として渡された数値も受け付ける。

        Returns:
            設定に成功した場合は ``True``。

        Raises:
            ValueError: ``start_height_mm`` が負の場合。
        """
        start_height_mm = float(start_height_mm)
        if start_height_mm < 0.0:
            raise ValueError("start_height_mm は 0.0 以上で指定してください。")

        self._start_height_mm = start_height_mm
        return True

    def set_return_to_start(self, return_to_start: bool) -> bool:
        """``write()`` 終了後の原点復帰動作の既定値を設定する。

        Args:
            return_to_start: 原点へ復帰する場合は ``True``。

        Returns:
            設定に成功した場合は ``True``。
        """
        self._return_to_start = bool(return_to_start)
        return True

    def set_new_line(self, new_line: bool) -> bool:
        """次回以降の ``write()`` で改行するかの既定値を設定する。

        最初の ``write()`` では改行せず、二回目以降の呼び出しで適用する。

        Args:
            new_line: 前回の文字列の次行または次列から書く場合は ``True``。
                ``False`` の場合は前回の次文字セルから続けて書く。

        Returns:
            設定に成功した場合は ``True``。
        """
        self._new_line = bool(new_line)
        return True

    def write(
        self,
        text: str,
        start_height_mm: Optional[float] = None,
        return_to_start: Optional[bool] = None,
        new_line: Optional[bool] = None,
    ) -> bool:
        """一行の文字列をロボットで書字する。

        呼び出し時の現在姿勢を作業空間の原点として保存し、文字列から得られた
        すべての筆画を順番に処理する。``start_height_mm`` は、開始姿勢が実際の
        書字面からどれだけ高い位置にあるかを表す。書字面は開始 Z 座標からこの値を
        引いて求め、ペン上げ位置は書字面に ``pen_lift_mm`` を加えて求める。

        最初の筆画では、開始姿勢が書字面上にある場合だけ、その場でペン上げ位置へ
        退避してから始点へ移動する。開始姿勢が既に書字面より高い場合は、その高さを
        保ったまま最初の始点へ移動する。二画目以降は、直前の終点でペンを上げ、
        次の始点へ空走し、書字面まで下ろしてから描画する。

        Args:
            text: 書く文字列。
            start_height_mm: ``write()`` 開始位置が書字面より高い量 [mm]。
                ``None`` の場合は :meth:`set_start_height_mm` の設定値を使用する。
            return_to_start: 書字終了後に ``write()`` 開始姿勢へ戻るか。
                ``None`` の場合は :meth:`set_return_to_start` の設定値を使用する。
                次回の論理的な書字位置には影響しない。
            new_line: 既に書字済みの場合、今回の文字列を次の行または次の列から
                書き始めるか。``None`` の場合は :meth:`set_new_line` の設定値を
                使用する。``False`` の場合は、前回の文字列に続く次文字セルを
                今回の書字原点とする。

        Returns:
            全筆画の書字と、指定された復帰動作に成功した場合は ``True``。
            ロボット操作が一つでも失敗した場合は ``False``。

        Raises:
            ValueError: ``start_height_mm`` が負の場合。
            RuntimeError: 現在 P 座標を取得できない場合、または取得値が 6 要素でない
                場合。
        """
        # write() で明示された値を、インスタンスに設定された既定値より優先する。
        if start_height_mm is None:
            start_height_mm = self._start_height_mm
        else:
            start_height_mm = float(start_height_mm)

        if return_to_start is None:
            return_to_start = self._return_to_start
        else:
            return_to_start = bool(return_to_start)

        if new_line is None:
            new_line = self._new_line
        else:
            new_line = bool(new_line)

        # ロボットへ接続・準備する前に、ロボット状態と無関係な入力値を検証する。
        # 空文字列であっても、負の高さ指定は呼び出し条件の誤りとして扱う。
        if start_height_mm < 0.0:
            raise ValueError("start_height_mm は 0.0 以上で指定してください。")

        if not self._connected or self._bcap is None:
            return False

        # 文字配置とロボット動作生成を分離し、ここでは配置済み筆画だけを受け取る。
        characters = self._layout.build(text)
        strokes = self._collect_strokes(characters)
        if len(strokes) == 0:
            return True

        # 呼び出し時の姿勢は、今回の物理的な復帰先として保持する。
        start_pose = self._read_pose()

        # 最初の write() 呼び出し時の姿勢を書字全体の原点として保持する。
        # return_to_start は物理的な復帰だけを制御し、次回の論理書字位置には
        # 影響させない。
        if self._document_origin is None:
            self._document_origin = list(start_pose)
            self._document_surface_z = float(start_pose[2]) - start_height_mm

        # 改行指定は、前回までに書字がある場合だけ今回の開始位置へ適用する。
        if new_line and self._has_written:
            if self.config.writing_direction == "vertical":
                self._cursor_y = 0.0
                if self.config.vertical_new_line_direction == "right_to_left":
                    self._cursor_x -= self.config.cell_width
                else:
                    self._cursor_x += self.config.cell_width
            else:
                self._cursor_x = 0.0
                if (
                    self.config.horizontal_new_line_direction
                    == "top_to_bottom"
                ):
                    self._cursor_y -= self.config.cell_height
                else:
                    self._cursor_y += self.config.cell_height

        workspace_origin = list(self._document_origin)
        cursor_point = FontPoint(
            x=self._cursor_x,
            y=self._cursor_y,
        )
        workspace_origin = self._point_to_pose(
            workspace_origin=workspace_origin,
            point=cursor_point,
            target_z=float(self._document_surface_z),
        )

        surface_z = float(self._document_surface_z)
        pen_up_z = surface_z + self.config.pen_lift_mm

        # 書字途中で失敗した場合に、明示的な緊急退避で使用する高さを保持する。
        self._write_in_progress = True
        self._emergency_pen_up_z = pen_up_z

        first_point = strokes[0].points[0]

        # 開始位置が書字面上の場合だけ、その場でペンを上げてから最初の始点へ向かう。
        if start_height_mm == 0.0:
            if not self._move_z(
                pose=start_pose,
                target_z=pen_up_z,
            ):
                return False
            first_travel_z = pen_up_z
        else:
            first_travel_z = float(start_pose[2])

        if not self._travel_to_point(
            workspace_origin=workspace_origin,
            point=first_point,
            target_z=first_travel_z,
        ):
            return False

        if not self._move_z_at_point(
            workspace_origin=workspace_origin,
            point=first_point,
            target_z=surface_z,
        ):
            return False

        # 筆画内ではペンを下ろしたまま描画し、筆画境界でのみ上げ下げを行う。
        for stroke_index, stroke in enumerate(strokes):
            if stroke_index > 0:
                # 直前の終点で上昇し、次の始点へ空走してから書字面へ下降する。
                stroke_start = stroke.points[0]

                previous_stroke = strokes[stroke_index - 1]
                previous_end = previous_stroke.points[-1]

                if not self._move_z_at_point(
                    workspace_origin=workspace_origin,
                    point=previous_end,
                    target_z=pen_up_z,
                ):
                    return False

                if not self._travel_to_point(
                    workspace_origin=workspace_origin,
                    point=stroke_start,
                    target_z=pen_up_z,
                ):
                    return False

                if not self._move_z_at_point(
                    workspace_origin=workspace_origin,
                    point=stroke_start,
                    target_z=surface_z,
                ):
                    return False

            if not self._draw_stroke(
                workspace_origin=workspace_origin,
                stroke=stroke,
                surface_z=surface_z,
            ):
                return False

        # 最終筆画の終了後も、復帰動作の有無にかかわらずペンを上げる。
        last_point = strokes[-1].points[-1]
        if not self._move_z_at_point(
            workspace_origin=workspace_origin,
            point=last_point,
            target_z=pen_up_z,
        ):
            return False

        if return_to_start:
            # XY 復帰中はペン上げ高さを維持し、最後に開始姿勢の Z へ戻す。
            if not self._move_absolute(
                target=self._pose_with_xyz(
                    base_pose=start_pose,
                    x=float(start_pose[0]),
                    y=float(start_pose[1]),
                    z=pen_up_z,
                ),
                speed=self.config.travel_speed,
                is_async=False,
            ):
                return False

            if not self._move_absolute(
                target=start_pose,
                speed=self.config.pen_speed,
                is_async=False,
            ):
                return False

        # 次回の write() が改行しない場合に使用する論理カーソルを、
        # 実際の最終筆画点ではなく次文字セルの原点へ進める。
        character_count = len(text)
        if self.config.writing_direction == "vertical":
            if self.config.vertical_direction == "top_to_bottom":
                self._cursor_y -= character_count * self.config.cell_height
            else:
                self._cursor_y += character_count * self.config.cell_height
        else:
            if self.config.line_direction == "right_to_left":
                self._cursor_x -= character_count * self.config.cell_width
            else:
                self._cursor_x += character_count * self.config.cell_width

        self._has_written = True
        self._write_in_progress = False
        self._emergency_pen_up_z = None
        return True

    def emergency_lift_pen(self):
        """書字失敗時に現在位置から予定したペン上げ高さへ退避する。

        コントローラエラーを解除して現在位置を再取得し、現在の XY と姿勢を維持した
        まま Z 方向だけを同期移動する。現在位置が予定したペン上げ高さより既に高い
        場合は、ペンを下げないよう現在の Z を維持する。退避処理の失敗はログへ記録する。

        Returns:
            緊急退避に成功した場合は ``True``。退避先が未設定、またはロボット操作に
            失敗した場合は ``False``。
        """
        if self._emergency_pen_up_z is None:
            return True

        self._logger.error("書字失敗のため、ペンの緊急退避を実行する。")

        try:
            if not self._bcap.reset_error():
                self._logger.error("緊急退避前のエラー解除に失敗した。")
                return False

            current_pose = self._read_pose()
            target_z = max(
                float(current_pose[2]),
                float(self._emergency_pen_up_z),
            )

            if not self._move_z(
                pose=current_pose,
                target_z=target_z,
            ):
                self._logger.error("ペンの緊急退避動作に失敗した。")
                return False

            self._logger.info("ペンを緊急退避した。 target_z=%s", target_z)
            return True
        except Exception:
            self._logger.exception("ペンの緊急退避中に例外が発生した。")
            return False

    @staticmethod
    def _collect_strokes(characters):
        """配置済み文字列から空でない筆画だけを取り出す。

        文字境界を越えて筆画を一次元の順序へ展開する。点を持たない筆画はロボット
        動作を生成できないため除外する。

        Args:
            characters: :class:`PositionedCharacter` のシーケンス。

        Returns:
            点を一つ以上持つ :class:`FontStrokePath` のリスト。
        """
        strokes = []
        for character in characters:
            for stroke in character.strokes:
                if len(stroke.points) > 0:
                    strokes.append(stroke)
        return strokes

    def _read_pose(self):
        """現在のロボット P 座標を 6 要素の浮動小数点リストとして取得する。

        Returns:
            X、Y、Z および姿勢成分からなる 6 要素のリスト。

        Raises:
            RuntimeError: 現在位置を取得できない場合、または取得値が 6 要素でない
                場合。
        """
        pose = self._bcap.get_curpos()
        if pose is False or pose is None:
            raise RuntimeError("現在P座標を取得できない。")
        values = list(pose)[:6]
        if len(values) != 6:
            raise RuntimeError("現在P座標が6要素ではない。")
        return [float(value) for value in values]

    def _point_to_pose(
        self,
        workspace_origin,
        point,
        target_z,
    ):
        """文字座標の点をロボットの絶対 P 座標へ変換する。

        文字座標に対して軸交換と軸符号を適用し、書字開始時の作業空間原点へ加算する。
        姿勢成分は原点姿勢を維持し、X、Y、Z のみを書き換える。

        Args:
            workspace_origin: 書字開始時に取得した 6 要素の基準姿勢。
            point: 変換対象の :class:`FontPoint`。
            target_z: 変換後の Z 座標 [mm]。

        Returns:
            ロボットへ送信する 6 要素の絶対 P 座標。
        """
        # 機体設置方向に応じて、文字座標系とロボット座標系の軸対応を切り替える。
        if self.config.robot_swap_xy:
            point_x = point.y
            point_y = point.x
        else:
            point_x = point.x
            point_y = point.y

        x = float(workspace_origin[0]) + point_x * self.config.robot_x_sign
        y = float(workspace_origin[1]) + point_y * self.config.robot_y_sign
        return self._pose_with_xyz(
            base_pose=workspace_origin,
            x=x,
            y=y,
            z=target_z,
        )

    @staticmethod
    def _pose_with_xyz(
        base_pose,
        x,
        y,
        z,
    ):
        """基準姿勢の姿勢成分を維持したまま XYZ 座標だけを置き換える。

        Args:
            base_pose: 基準とする 6 要素の P 座標。
            x: 置き換える X 座標。
            y: 置き換える Y 座標。
            z: 置き換える Z 座標。

        Returns:
            XYZ を更新した 6 要素の P 座標。
        """
        target = list(base_pose)[:6]
        target[0] = float(x)
        target[1] = float(y)
        target[2] = float(z)
        return target

    def _move_z(
        self,
        pose,
        target_z,
    ):
        """指定姿勢の XY と姿勢を維持し、Z 方向だけを同期移動する。

        Args:
            pose: 移動基準とする 6 要素の P 座標。
            target_z: 移動先の Z 座標 [mm]。

        Returns:
            移動指令に成功した場合は ``True``、失敗した場合は ``False``。
        """
        target = self._pose_with_xyz(
            base_pose=pose,
            x=float(pose[0]),
            y=float(pose[1]),
            z=target_z,
        )
        return self._move_absolute(
            target=target,
            speed=self.config.pen_speed,
            is_async=False,
        )

    def _move_z_at_point(
        self,
        workspace_origin,
        point,
        target_z,
    ):
        """文字上の指定点でペンを Z 方向へ同期移動する。

        Args:
            workspace_origin: 書字開始時の基準姿勢。
            point: XY 位置を決める文字座標上の点。
            target_z: 移動先の Z 座標 [mm]。

        Returns:
            移動指令に成功した場合は ``True``、失敗した場合は ``False``。
        """
        target = self._point_to_pose(
            workspace_origin=workspace_origin,
            point=point,
            target_z=target_z,
        )
        return self._move_absolute(
            target=target,
            speed=self.config.pen_speed,
            is_async=False,
        )

    def _travel_to_point(
        self,
        workspace_origin,
        point,
        target_z,
    ):
        """ペンを下ろさず、指定高さを保って文字上の点へ同期移動する。

        Args:
            workspace_origin: 書字開始時の基準姿勢。
            point: 空走先となる文字座標上の点。
            target_z: 空走中に維持する Z 座標 [mm]。

        Returns:
            移動指令に成功した場合は ``True``、失敗した場合は ``False``。
        """
        target = self._point_to_pose(
            workspace_origin=workspace_origin,
            point=point,
            target_z=target_z,
        )
        return self._move_absolute(
            target=target,
            speed=self.config.travel_speed,
            is_async=False,
        )

    def _draw_stroke(
        self,
        workspace_origin,
        stroke,
        surface_z,
    ):
        """一つの筆画を同一 Z 座標上の連続直線として描画する。

        呼び出し時点でペン先は筆画の始点かつ書字面上にあることを前提とする。
        始点は既に到達済みであるため、二点目以降だけを非同期で投入する。すべての
        目標を投入した後、完了待ちを一度だけ行うことで筆画内の連続性を保つ。

        Args:
            workspace_origin: 書字開始時の基準姿勢。
            stroke: 描画対象の :class:`FontStrokePath`。
            surface_z: 書字面の Z 座標 [mm]。

        Returns:
            描画速度の設定、全目標の投入および完了待ちに成功した場合は ``True``。
            いずれかが失敗した場合は ``False``。点が一つ以下の筆画は動作不要として
            ``True`` を返す。
        """
        if len(stroke.points) <= 1:
            return True

        if not self._bcap.set_speed(self.config.drawing_speed):
            return False

        # 始点は既に到達済みであるため、二点目以降だけを連続投入する。
        for point in stroke.points[1:]:
            target = self._point_to_pose(
                workspace_origin=workspace_origin,
                point=point,
                target_z=surface_z,
            )

            if not self._bcap.move_L(
                target,
                coord_type="P",
                path_blend="@P",
                is_async=True,
            ):
                return False

        # 筆画単位で完了を待ち、次のペン上げ動作との順序を保証する。
        return self._bcap.wait_for_complete()

    def _move_absolute(
        self,
        target,
        speed,
        is_async,
    ):
        """速度を設定し、絶対 P 座標への直線移動を実行する。

        Args:
            target: 移動先となる 6 要素の絶対 P 座標。
            speed: 移動前に設定する速度。
            is_async: 非同期移動として投入するか。

        Returns:
            速度設定と移動指令に成功した場合は ``True``。いずれかが失敗した場合は
            ``False``。
        """
        if not self._bcap.set_speed(speed):
            return False

        return self._bcap.move_L(
            list(target)[:6],
            coord_type="P",
            path_blend="@P",
            is_async=is_async,
        )


def main():
    """実機接続を用いた一行書字の単体実行例を実行する。

    設定値から writer を生成し、接続、各準備操作、書字の順に個別実行する。
    終了時も、必要なペン退避、アーム権限返却、切断を個別に実行する。
    """
    config = FontBcapCobottaWriterConfig(
        kanjivg_directory=Path(
            # r"C:\Users\nakada\zaiene_dev\glyph_motion\data\kanjiVG"
            r"C:\Users\nakada\Desktop\kanji",
        ),
        host="10.170.10.36",  # cobotta2
        # host="10.170.10.53",  # cobotta3
        port=5007,
        # 書字ワークスペースの大きさ
        workspace_width=200.0,
        # workspace_height=10.0,
        workspace_height=100.0,
        # 1文字に割り当てるセルの幅（mm）。
        cell_width=8.0,
        # 1文字に割り当てるセルの高さ（mm）。
        cell_height=8.0,
        # セル内に描画する文字の高さ（mm）。
        character_height=7.0,
        # 曲線を直線分割するときの分割数。
        curve_division=16,
        # 筆画間でペンを持ち上げる高さ（mm）。
        #pen_lift_mm=1.7,
        pen_lift_mm=17,
        # 文字座標Xをロボット座標へ変換するときの符号。
        robot_x_sign=1.0,
        # 文字座標Yをロボット座標へ変換するときの符号。
        robot_y_sign=1.0,
        # 文字座標のX軸とY軸をロボット座標へ割り当てる際に入れ替えるかどうか。
        robot_swap_xy=True,
        # 横書き時の文字進行方向。縦書き時には使用しない。
        line_direction="left_to_right",
        # line_direction="right_to_left",
        # 文字列を横書きまたは縦書きのどちらで配置するか。
        # writing_direction="horizontal",
        writing_direction="vertical",
        # 縦書き時の文字進行方向。横書き時には使用しない。
        vertical_direction="top_to_bottom",
        # vertical_direction="bottom_to_top",
        # 横書き時の改行方向。
        horizontal_new_line_direction="top_to_bottom",
        # horizontal_new_line_direction="bottom_to_top",
        # 縦書き時の改列方向。
        vertical_new_line_direction="right_to_left",
        # vertical_new_line_direction="left_to_right",
        # 各文字をセル内で左右反転するかどうか。
        # mirror_horizontal=False,
        mirror_horizontal=True,
        # 各文字をセル内で上下反転するかどうか。
        mirror_vertical=False,
        # 筆画を描画するときのロボット速度。
        drawing_speed=35,
        # ペンを上げた状態で移動するときのロボット速度。
        travel_speed=40,
        # ペンを上下させるときのロボット速度。
        pen_speed=20,
        # ロボット動作の加速度設定。
        accel=100,
        # ロボット動作の減速度設定。
        decel=100,
    )

    writer = FontBcapCobottaWriter(config=config)

    try:
        if not writer.connect():
            raise RuntimeError("COBOTTAへ接続できない。")
        if not writer.reset_error():
            raise RuntimeError("COBOTTAのエラー解除に失敗した。")
        if not writer.take_arm():
            raise RuntimeError("COBOTTAのアーム権限取得に失敗した。")
        if not writer.motor_on():
            raise RuntimeError("COBOTTAのモータ投入に失敗した。")
        if not writer.set_accel():
            raise RuntimeError("COBOTTAの加速度設定に失敗した。")
        if not writer.set_decel():
            raise RuntimeError("COBOTTAの減速度設定に失敗した。")

        if not writer.write(
            text="島根大学 尾原研究室",
            # text="島根大学",
            start_height_mm=1.0,
            return_to_start=True,
        ):
            raise RuntimeError("COBOTTAの書字に失敗した。")
    finally:
        writer.emergency_lift_pen()
        writer.give_arm()
        writer.disconnect()


if __name__ == "__main__":
    main()
