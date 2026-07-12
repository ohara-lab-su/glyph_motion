#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KanjiVG の文字ストロークを固定サイズの一行レイアウトへ配置する。

このモジュールは、文字列を文字単位のセルへ割り当て、KanjiVG から取得した
ストローク座標を各セルの中央へ平行移動する。生成される座標列は
``FontStrokePath`` として保持され、後段の軌道生成処理やロボット制御処理へ
渡すことを想定している。

本モジュールの責務は幾何学的な配置に限定される。ロボットへの接続、姿勢変換、
ペンの上げ下げ、速度指定などの装置依存処理は行わない。これにより、文字配置の
検証と実機制御を分離し、同一のレイアウト結果を異なる出力装置で再利用できる。

配置処理では、作業空間を固定幅のセルに分割し、文字列中の各文字を一つのセルへ
対応付ける。文字の実幅がセル幅より小さい場合は水平方向に中央揃えし、文字高は
指定された ``character_height`` を基準として垂直方向に中央揃えする。空白文字も
一つのセルを消費するが、ストロークは生成しない。
"""

from pathlib import Path
from typing import List

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokePath
from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader


class PositionedCharacter:
    """一つの文字セルへ配置済みの文字情報を保持する。

    文字そのものに加え、入力文字列中の位置、割り当てられたセルの原点、
    およびセル座標系へ変換済みのストローク列をまとめて保持する。
    空白文字では ``strokes`` が空になるが、文字列中の位置とセル割り当ては
    他の文字と同様に保持される。

    Args:
        character: 配置対象の一文字。
        index: 入力文字列中のゼロ始まりの文字位置。
        cell_origin_x: 割り当てられたセル左下原点の X 座標。
        cell_origin_y: 割り当てられたセル左下原点の Y 座標。
        strokes: セル内へ配置済みのストローク列。

    Attributes:
        character: 配置対象の一文字。
        index: 入力文字列中のゼロ始まりの文字位置。
        cell_origin_x: セル原点の X 座標。
        cell_origin_y: セル原点の Y 座標。
        strokes: 配置済みストローク列。
    """

    def __init__(
        self,
        character: str,
        index: int,
        cell_origin_x: float,
        cell_origin_y: float,
        strokes: List[FontStrokePath],
    ) -> None:
        """配置済み文字情報を初期化する。

        Args:
            character: 配置対象の一文字。
            index: 入力文字列中のゼロ始まりの文字位置。
            cell_origin_x: 割り当てられたセル左下原点の X 座標。
            cell_origin_y: 割り当てられたセル左下原点の Y 座標。
            strokes: セル内へ配置済みのストローク列。
        """
        # 座標値は生成元の数値型に依存させず、後段で一貫して扱えるよう
        # float へ正規化して保持する。
        self.character = character
        self.index = index
        self.cell_origin_x = float(cell_origin_x)
        self.cell_origin_y = float(cell_origin_y)
        self.strokes = strokes


class FontLineLayout:
    """固定作業空間内に一行分の文字ストロークを配置する。

    作業空間を ``cell_width`` と ``cell_height`` で定義される固定セルに分割し、
    入力文字列の各文字を順番に割り当てる。文字データは
    ``FontKanjiVGStrokeLoader`` から取得し、セル中央へ移動した後、必要に応じて
    水平方向の鏡像変換を適用する。

    このクラスは、文字列から「どの文字が、どのセルに、どの座標列として置かれる
    か」を確定するレイアウト層である。後段のモーション生成処理が文字幅や余白を
    再計算する必要がないよう、配置結果を絶対座標で返す。

    Args:
        kanjivg_directory: KanjiVG の SVG ファイルを格納したディレクトリ。
        workspace_width: 一行の配置に使用できる作業空間の幅。
        workspace_height: 作業空間の高さ。
        cell_width: 一文字へ割り当てるセルの幅。
        cell_height: 一文字へ割り当てるセルの高さ。
        character_height: KanjiVG から読み込む文字の基準高さ。
        curve_division: ベジェ曲線を折れ線へ分割するときの分割数。
        line_direction: 横書き時の進行方向。``left_to_right`` または
            ``right_to_left`` を指定する。
        writing_direction: 文字列を横書きまたは縦書きのどちらで配置するか。
        vertical_direction: 縦書き時の進行方向。``top_to_bottom`` または
            ``bottom_to_top`` を指定する。
        mirror_horizontal: 各セル内の文字を水平方向に反転するかどうか。
        mirror_vertical: 各セル内の文字を垂直方向に反転するかどうか。

    Raises:
        ValueError: 作業空間、セル寸法、文字高が正でない場合。
        ValueError: セル寸法が作業空間を超える場合。
        ValueError: 文字高がセル高を超える場合。
        ValueError: 配置方向の指定が未対応の値である場合。
    """

    def __init__(
        self,
        kanjivg_directory: Path,
        workspace_width: float,
        workspace_height: float,
        cell_width: float,
        cell_height: float,
        character_height: float,
        curve_division: int = 16,
        line_direction: str = "left_to_right",
        writing_direction: str = "horizontal",
        vertical_direction: str = "top_to_bottom",
        mirror_horizontal: bool = False,
        mirror_vertical: bool = False,
    ) -> None:
        """レイアウト条件と KanjiVG ローダーを初期化する。

        初期化時に、配置計算の前提となる寸法と方向指定を検証する。不正な設定を
        ``build`` 実行時まで持ち越さないことで、レイアウト失敗の原因を設定箇所で
        明確にする。

        Args:
            kanjivg_directory: KanjiVG の SVG ファイルを格納したディレクトリ。
            workspace_width: 一行の配置に使用できる作業空間の幅。
            workspace_height: 作業空間の高さ。
            cell_width: 一文字へ割り当てるセルの幅。
            cell_height: 一文字へ割り当てるセルの高さ。
            character_height: KanjiVG から読み込む文字の基準高さ。
            curve_division: ベジェ曲線を折れ線へ分割するときの分割数。
            line_direction: 横書き時の進行方向。
            writing_direction: 横書きまたは縦書きの指定。
            vertical_direction: 縦書き時の進行方向。
            mirror_horizontal: 各セル内の文字を水平方向に反転するかどうか。
            mirror_vertical: 各セル内の文字を垂直方向に反転するかどうか。

        Raises:
            ValueError: 寸法値が正でない場合。
            ValueError: セル寸法が作業空間を超える場合。
            ValueError: ``character_height`` が ``cell_height`` を超える場合。
            ValueError: 書字方向または進行方向が未対応の値である場合。
        """
        # ゼロ以下の寸法ではセル分割や中央揃えの意味が成立しないため、
        # レイアウト処理へ入る前に入力条件として排除する。
        if workspace_width <= 0.0:
            raise ValueError("workspace_width は正の値である必要がある。")
        if workspace_height <= 0.0:
            raise ValueError("workspace_height は正の値である必要がある。")
        if cell_width <= 0.0:
            raise ValueError("cell_width は正の値である必要がある。")
        if cell_height <= 0.0:
            raise ValueError("cell_height は正の値である必要がある。")
        if character_height <= 0.0:
            raise ValueError("character_height は正の値である必要がある。")

        # セル自体が作業空間を超える設定では、文字数が一文字であっても
        # レイアウト結果が作業範囲外へ出る。縮小処理は行わないため、
        # 初期化時点で設定不整合として扱う。
        if cell_width > workspace_width:
            raise ValueError("cell_width は workspace_width 以下である必要がある。")
        if cell_height > workspace_height:
            raise ValueError("cell_height は workspace_height 以下である必要がある。")

        # 文字高がセル高を超えると、上下中央揃えを行ってもセル外へはみ出す。
        # 本クラスでは縮小処理を行わないため、設定不整合として扱う。
        if character_height > cell_height:
            raise ValueError("character_height は cell_height 以下である必要がある。")

        # 数値入力を float に統一し、整数で指定された場合も除算結果や座標計算を
        # 同じ規則で扱えるようにする。
        self.workspace_width = float(workspace_width)
        self.workspace_height = float(workspace_height)
        self.cell_width = float(cell_width)
        self.cell_height = float(cell_height)
        self.character_height = float(character_height)

        # writing_direction は文字列を並べる軸だけを決定する。横書きと縦書きで
        # 進行方向の語彙を混在させないため、左右方向と上下方向は別々に保持する。
        if writing_direction not in ("horizontal", "vertical"):
            raise ValueError(
                "writing_direction は horizontal または vertical を指定してください。"
            )

        if line_direction not in ("left_to_right", "right_to_left"):
            raise ValueError(
                "line_direction は left_to_right または right_to_left を指定してください。"
            )

        if vertical_direction not in ("top_to_bottom", "bottom_to_top"):
            raise ValueError(
                "vertical_direction は top_to_bottom または bottom_to_top を指定してください。"
            )

        self.writing_direction = writing_direction
        self.line_direction = line_direction
        self.vertical_direction = vertical_direction
        self.mirror_horizontal = bool(mirror_horizontal)
        self.mirror_vertical = bool(mirror_vertical)

        # ローダーには文字高だけを与え、文字間隔はレイアウト側の固定セルで管理する。
        # これにより、KanjiVG 側の advance width とセル側の余白計算を分離する。
        self._loader = FontKanjiVGStrokeLoader(
            kanjivg_directory=kanjivg_directory,
            height=self.character_height,
            spacing=0.0,
            curve_division=curve_division,
        )

    @property
    def capacity(self) -> int:
        """作業空間に収容できる最大セル数を返す。

        横書きでは作業空間幅をセル幅で、縦書きでは作業空間高さをセル高で
        整数除算し、書字方向へ完全に収まるセルだけを数える。端数として残る
        領域は、一文字分のセルとしては使用しない。

        Returns:
            作業空間へ配置できる最大文字数。
        """
        if self.writing_direction == "horizontal":
            return int(self.workspace_width // self.cell_width)
        return int(self.workspace_height // self.cell_height)

    def build(
        self,
        text: str,
    ) -> List[PositionedCharacter]:
        """文字列を固定セルへ割り当て、配置済みストローク列を生成する。

        各文字について、次の順序で配置を行う。

        1. 文字列中の位置から使用するセル番号を決定する。
        2. 書字方向に応じてセル原点を求める。
        3. 空白文字では空のストローク列を生成する。
        4. KanjiVG から文字ストロークと文字幅を読み込む。
        5. 文字をセル中央へ移動するためのオフセットを求める。
        6. 各点へ平行移動と必要な鏡像変換を適用する。
        7. 配置済み文字情報として結果へ追加する。

        入力文字列の順序は ``PositionedCharacter.index`` に保持される。
        返却リストの順序と各文字の筆順は常に入力順を維持し、進行方向の指定は
        各文字へ割り当てるセル原点の増分符号だけを変更する。

        Args:
            text: 配置する文字列。空白文字も一文字分のセルを使用する。

        Returns:
            入力文字列の順序で並んだ配置済み文字情報のリスト。

        Raises:
            ValueError: 文字数が作業空間の収容数を超える場合。
            ValueError: 読み込んだ文字幅がセル幅を超える場合。
        """
        # 文字単位の縮小や折り返しは行わない。入力全体が一行へ収まることを
        # 先に確認し、途中まで配置した不完全な結果を返さない。
        if len(text) > self.capacity:
            raise ValueError(
                "文字数が作業空間の収容数を超えている: {} > {}".format(
                    len(text),
                    self.capacity,
                )
            )

        positioned_characters = []

        for character_index, character in enumerate(text):
            # 先頭文字は常に作業原点のセルへ置く。進行方向を反転するときも
            # 作業空間の反対端へ先頭文字を飛ばさず、セル間の増分符号だけを変える。
            # これにより、書字開始位置と最初の文字位置の関係を方向に依存させない。
            cell_index = character_index

            if self.writing_direction == "horizontal":
                if self.line_direction == "left_to_right":
                    cell_step = self.cell_width
                else:
                    cell_step = -self.cell_width
                cell_origin_x = float(cell_index) * cell_step
                cell_origin_y = 0.0
            else:
                cell_origin_x = 0.0
                if self.vertical_direction == "top_to_bottom":
                    cell_step = -self.cell_height
                else:
                    cell_step = self.cell_height
                cell_origin_y = float(cell_index) * cell_step

            # 空白文字は文字間隔として意味を持つため、セル自体は消費する。
            # 一方で描画対象の点列は存在しないので、ローダーを呼ばず空のまま保持する。
            if character == " ":
                positioned_characters.append(
                    PositionedCharacter(
                        character=character,
                        index=character_index,
                        cell_origin_x=cell_origin_x,
                        cell_origin_y=cell_origin_y,
                        strokes=[],
                    )
                )
                continue

            # KanjiVG の文字データは、指定文字高へ正規化されたストローク列と、
            # その文字が占める実幅として取得する。
            character_glyph, advance_width = self._loader.load_character(
                character=character,
            )

            # このクラスでは文字幅をセルへ合わせて再縮小しない。
            # セル幅を超える文字は、設定または入力データの不整合として明示する。
            if advance_width > self.cell_width:
                raise ValueError(
                    "文字幅が文字空間を超えている: {}: {} > {}".format(
                        character,
                        advance_width,
                        self.cell_width,
                    )
                )

            # 水平方向は実際の文字幅を基準に左右余白を等分する。
            # 垂直方向はローダーへ指定した文字高を基準に上下余白を等分する。
            x_offset = cell_origin_x + (self.cell_width - advance_width) / 2.0
            y_offset = cell_origin_y + (self.cell_height - self.character_height) / 2.0

            strokes = []
            for stroke in character_glyph:
                points = []
                for point in stroke:
                    # KanjiVG の局所 X 座標を、セル中央へ移動した作業空間座標へ変換する。
                    positioned_x = point.x + x_offset

                    if self.mirror_horizontal:
                        # 反転は作業空間全体ではなく、現在のセル内を基準に行う。
                        # そのため、他のセルの位置や文字間隔には影響しない。
                        local_x = positioned_x - cell_origin_x
                        positioned_x = cell_origin_x + self.cell_width - local_x

                    # Y 座標にも上下中央揃えのオフセットを加える。上下反転は
                    # 作業空間全体ではなく、現在のセル内を基準に適用する。
                    positioned_y = point.y + y_offset

                    if self.mirror_vertical:
                        local_y = positioned_y - cell_origin_y
                        positioned_y = cell_origin_y + self.cell_height - local_y

                    # 座標だけを変換し、点の順序とストローク方向は保持する。
                    points.append(
                        FontPoint(
                            x=positioned_x,
                            y=positioned_y,
                        )
                    )

                # 空のストロークは後段の軌道生成に意味を持たないため除外する。
                # 有効な点を含むストロークだけを配置結果へ残す。
                if len(points) > 0:
                    strokes.append(FontStrokePath(points=points))

            positioned_characters.append(
                PositionedCharacter(
                    character=character,
                    index=character_index,
                    cell_origin_x=cell_origin_x,
                    cell_origin_y=cell_origin_y,
                    strokes=strokes,
                )
            )

        return positioned_characters
