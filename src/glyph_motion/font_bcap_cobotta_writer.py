#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KanjiVG のストローク点列を、COBOTTA の絶対P目標として連続投入する。

設計:
- write() は一行だけを書く。
- 作業空間と文字空間の大きさは固定する。
- 一つのストローク内は、同じZで絶対P目標を NEXT 指定で連続投入する。
- ストローク間および文字間は、ペンを上げた状態で次のストローク始点へ
  LINE移動を一回だけ行う。
- 相対移動用 robo_dmove_P() は使用しない。
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
    """一行書字に必要な最小設定を保持する。"""

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
        # 横書き・縦書き
        line_direction="left_to_right",
        # 横書き・縦書き
        writing_direction="horizontal",
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
        self.mirror_horizontal = bool(mirror_horizontal)
        self.mirror_vertical = bool(mirror_vertical)
        self.drawing_speed = int(drawing_speed)
        self.travel_speed = int(travel_speed)
        self.pen_speed = int(pen_speed)
        self.accel = int(accel)
        self.decel = int(decel)


class FontBcapCobottaWriter:
    """固定作業空間へ一行の文字列を書く。"""

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
        self._prepared = False

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
            mirror_horizontal=config.mirror_horizontal,
            mirror_vertical=config.mirror_vertical,
        )

    def connect(self):
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

    def prepare(self):
        if not self._connected:
            if not self.connect():
                return False

        if not self._bcap.reset_error():
            return False
        if not self._bcap.take_arm():
            return False
        if not self._bcap.motor_on():
            return False
        if not self._bcap.set_accel(self.config.accel):
            return False
        if not self._bcap.set_decel(self.config.decel):
            return False

        self._prepared = True
        return True

    def close(self):
        if self._bcap is None:
            return

        try:
            if self._prepared:
                self._bcap.give_arm()
        finally:
            self._prepared = False

        if self._owns_bcap:
            self._bcap.disconnect()
            self._connected = False

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
        mirror_horizontal: Optional[bool] = None,
        mirror_vertical: Optional[bool] = None,
        drawing_speed: Optional[int] = None,
        travel_speed: Optional[int] = None,
        pen_speed: Optional[int] = None,
        accel: Optional[int] = None,
        decel: Optional[int] = None,
    ) -> bool:
        """通信設定以外の書字設定を更新する。

        None が指定された項目は現在値を維持する。
        レイアウト関連項目を変更した場合は FontLineLayout を再構築する。
        """
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

        if mirror_horizontal is not None:
            new_mirror_horizontal = bool(mirror_horizontal)
            layout_changed = True

        if mirror_vertical is not None:
            new_mirror_vertical = bool(mirror_vertical)
            layout_changed = True

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

        if self._prepared:
            if accel is not None:
                if not self._bcap.set_accel(self.config.accel):
                    return False

            if decel is not None:
                if not self._bcap.set_decel(self.config.decel):
                    return False

        return True

    def write(
        self,
        text: str,
        start_height_mm: float = 0.0,
        return_to_start: bool = True,
    ) -> bool:
        """一行の文字列を書く。

        Args:
            text: 書く文字列。
            start_height_mm: write() 開始位置が底面より高い量 [mm]。
                0.0 の場合は開始位置を底面とみなす。
            return_to_start: 終了後に write() 開始位置へ戻るか。
        """
        if not self._prepared:
            if not self.prepare():
                return False

        characters = self._layout.build(text)
        strokes = self._collect_strokes(characters)
        if len(strokes) == 0:
            return True

        start_pose = self._read_pose()
        workspace_origin = list(start_pose)

        start_height_mm = float(start_height_mm)
        if start_height_mm < 0.0:
            raise ValueError("start_height_mm は 0.0 以上で指定してください。")

        surface_z = float(start_pose[2]) - start_height_mm
        pen_up_z = surface_z + self.config.pen_lift_mm

        first_point = strokes[0].points[0]

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

        for stroke_index, stroke in enumerate(strokes):
            if stroke_index > 0:
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

        last_point = strokes[-1].points[-1]
        if not self._move_z_at_point(
            workspace_origin=workspace_origin,
            point=last_point,
            target_z=pen_up_z,
        ):
            return False

        if return_to_start:
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

        return True

    @staticmethod
    def _collect_strokes(characters):
        strokes = []
        for character in characters:
            for stroke in character.strokes:
                if len(stroke.points) > 0:
                    strokes.append(stroke)
        return strokes

    def _read_pose(self):
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
        if len(stroke.points) <= 1:
            return True

        if not self._bcap.set_speed(self.config.drawing_speed):
            return False

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

        return self._bcap.wait_for_complete()

    def _move_absolute(
        self,
        target,
        speed,
        is_async,
    ):
        if not self._bcap.set_speed(speed):
            return False

        return self._bcap.move_L(
            list(target)[:6],
            coord_type="P",
            path_blend="@P",
            is_async=is_async,
        )


def main():
    """底面開始で単体テストを行う。"""
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
        # ロボット座標系をxy入れ替え
        robot_swap_xy=True,
        # 横書き・縦書き
        line_direction="left_to_right",
        # 横書き・縦書き
        writing_direction="horizontal",
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
    )

    writer = FontBcapCobottaWriter(config=config)

    try:
        if not writer.connect():
            raise RuntimeError("COBOTTAへ接続できない。")
        if not writer.prepare():
            raise RuntimeError("COBOTTAの書字準備に失敗した。")

        ret = writer.write(
            # text="島根大学 尾原研究室",
            text="島根大学",
            start_height_mm=1.0,
            return_to_start=True,
        )
    finally:
        writer.close()


if __name__ == "__main__":
    main()
