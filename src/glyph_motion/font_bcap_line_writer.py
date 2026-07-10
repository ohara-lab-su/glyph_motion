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


class CobottaFontLineWriterConfig:
    """一行書字に必要な最小設定を保持する。"""

    def __init__(
        self,
        kanjivg_directory,
        host="10.170.10.53",
        port=5007,
        workspace_width=160.0,
        workspace_height=40.0,
        cell_width=40.0,
        cell_height=40.0,
        character_height=36.0,
        curve_division=16,
        pen_lift_mm=1.0,
        robot_x_sign=1.0,
        robot_y_sign=1.0,
        robot_swap_xy=False,
        drawing_speed=20,
        travel_speed=40,
        pen_speed=20,
        accel=100,
        decel=100,
    ):
        # type: (Path, str, int, float, float, float, float, float, int, float, float, float, bool, int, int, int, int, int) -> None
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
        self.drawing_speed = int(drawing_speed)
        self.travel_speed = int(travel_speed)
        self.pen_speed = int(pen_speed)
        self.accel = int(accel)
        self.decel = int(decel)


class CobottaFontLineWriter:
    """固定作業空間へ一行の文字列を書く。"""

    def __init__(
        self,
        config,
        bcap=None,
        logger=None,
    ):
        # type: (CobottaFontLineWriterConfig, Optional[CobottaBcap], Optional[Any]) -> None
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
        )

    def connect(self):
        # type: () -> bool
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
        # type: () -> bool
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
        # type: () -> None
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

    def write(
        self,
        text,
        start_pen_up=False,
        return_to_start=True,
    ):
        # type: (str, bool, bool) -> bool
        """一行の文字列を書く。デフォルトは底面開始である。"""
        if not self._prepared:
            if not self.prepare():
                return False

        characters = self._layout.build(text)
        strokes = self._collect_strokes(characters)
        if len(strokes) == 0:
            return True

        start_pose = self._read_pose()
        workspace_origin = list(start_pose)

        if start_pen_up:
            surface_z = float(start_pose[2]) - self.config.pen_lift_mm
        else:
            surface_z = float(start_pose[2])

        pen_up_z = surface_z + self.config.pen_lift_mm

        first_point = strokes[0].points[0]

        if not start_pen_up:
            if not self._move_z(
                pose=start_pose,
                target_z=pen_up_z,
            ):
                return False

        if not self._travel_to_point(
            workspace_origin=workspace_origin,
            point=first_point,
            target_z=pen_up_z,
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

            if not start_pen_up:
                if not self._move_absolute(
                    target=start_pose,
                    speed=self.config.pen_speed,
                    is_async=False,
                ):
                    return False

        return True

    @staticmethod
    def _collect_strokes(characters):
        # type: (List[PositionedCharacter]) -> List[FontStrokePath]
        strokes = []  # type: List[FontStrokePath]
        for character in characters:
            for stroke in character.strokes:
                if len(stroke.points) > 0:
                    strokes.append(stroke)
        return strokes

    def _read_pose(self):
        # type: () -> List[float]
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
        # type: (Sequence[float], FontPoint, float) -> List[float]
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
    def _pose_with_xyz(base_pose, x, y, z):
        # type: (Sequence[float], float, float, float) -> List[float]
        target = list(base_pose)[:6]
        target[0] = float(x)
        target[1] = float(y)
        target[2] = float(z)
        return target

    def _move_z(self, pose, target_z):
        # type: (Sequence[float], float) -> bool
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
        # type: (Sequence[float], FontPoint, float) -> bool
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
        # type: (Sequence[float], FontPoint, float) -> bool
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
        # type: (Sequence[float], FontStrokePath, float) -> bool
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
        # type: (Sequence[float], int, bool) -> bool
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
    config = CobottaFontLineWriterConfig(
        kanjivg_directory=Path(
            # r"C:\Users\nakada\zaiene_dev\glyph_motion\data\kanjiVG"
            r"C:\Users\nakada\Desktop\kanji",
        ),
        host="10.170.10.36",  # cobotta2
        # host="10.170.10.53",  # cobotta3
        # ワークスペースの大きさ
        workspace_width=10.0,
        workspace_height=10.0,
        # 一文字の箱の大きさ
        # cell_width=40.0,
        # cell_height=40.0,
        cell_width=8.0,
        cell_height=8.0,
        # 箱の中の文字の高さ
        character_height=7.0,
        pen_lift_mm=1.0,
        curve_division=16,
        robot_swap_xy=True,
    )

    writer = CobottaFontLineWriter(config=config)

    try:
        if not writer.connect():
            raise RuntimeError("COBOTTAへ接続できない。")
        if not writer.prepare():
            raise RuntimeError("COBOTTAの書字準備に失敗した。")
        if not writer.write(
            text="島根",
            start_pen_up=False,
            return_to_start=True,
        ):
            raise RuntimeError("書字に失敗した。")
    finally:
        writer.close()


if __name__ == "__main__":
    main()
