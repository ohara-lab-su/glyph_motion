#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com
-----------------
font_bcap_cobotta_writer.py
COBOTTA b-CAP を用いて筆順付き文字を書く制御クラスを定義する。
    ↓
font_robot_writer.py
文字列をロボット筆記用の相対移動命令へ変換する簡易 I/F を定義する。
    ↓
font_robot_motion_builder.py
筆順付き stroke データを、ロボット向けの相対移動命令へ変換する。
    ↓
font_motion_builder.py
中心線データまたは筆順付き stroke データをXY相対移動命令へ変換する。(非ロボット依存)
-----------------

中心線データまたは筆順付き stroke データをXY相対移動命令へ変換する。

このモジュールは FontCenterlineGlyph または FontStrokeGlyph を入力として受け取り、
FontMotionCommand の列を出力する。

FontCenterlineGlyph は、太い文字から抽出された細い中心線である。
この線を点列として順にたどり、現在位置から次点までの差分 dx, dy を作る。

FontStrokeGlyph は、筆順付きの描画単位である。
FontStrokeGlyph の各 FontStrokePath は、一回ペンを下ろして書く単位である。

このモジュールでは、ロボット固有APIは呼ばない。
ここで作るのは、既存のロボット制御プログラムへ渡す前段の
抽象的なXY相対移動命令である。
"""

from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from glyph_motion.lib.font_centerline_cleaner import FontCenterlineCleaner
from glyph_motion.lib.font_geometry import FontCenterlineGlyph
from glyph_motion.lib.font_geometry import FontCenterlinePath
from glyph_motion.lib.font_geometry import FontMotionCommand
from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokeGlyph


class FontMotionBuilder:
    """中心線または筆順付き stroke をXY相対移動命令列へ変換するクラスである。"""

    def __init__(
        self,
        centerline_cleaner: Optional[FontCenterlineCleaner] = None,
    ) -> None:
        """中心線整理器を受け取って初期化する。

        Args:
            centerline_cleaner: 中心線を命令化前に整理するためのクラスである。
        """
        self._centerline_cleaner = centerline_cleaner

    def build(
        self,
        centerline_glyph: FontCenterlineGlyph,
    ) -> List[FontMotionCommand]:
        """中心線からXY相対移動命令列を作る。"""
        working_centerline_glyph = centerline_glyph

        if self._centerline_cleaner is not None:
            working_centerline_glyph = self._centerline_cleaner.clean(
                centerline_glyph=centerline_glyph,
            )

        commands: List[FontMotionCommand] = []

        current_point = FontPoint(
            x=0.0,
            y=0.0,
        )

        for centerline_path in working_centerline_glyph:
            if len(centerline_path) == 0:
                continue

            start_point = centerline_path.points[0]

            move_to_start = FontMotionCommand(
                pen=0.0,
                dx=start_point.x - current_point.x,
                dy=start_point.y - current_point.y,
            )
            commands.append(move_to_start)

            current_point = start_point

            pen_down = FontMotionCommand(
                pen=1.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_down)

            for point_index in range(1, len(centerline_path.points)):
                next_point = centerline_path.points[point_index]

                command = FontMotionCommand(
                    pen=1.0,
                    dx=next_point.x - current_point.x,
                    dy=next_point.y - current_point.y,
                )
                commands.append(command)

                current_point = next_point

            pen_up = FontMotionCommand(
                pen=0.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_up)

        return commands

    def build_from_stroke(
        self,
        stroke_glyph: FontStrokeGlyph,
    ) -> List[FontMotionCommand]:
        """筆順付き stroke データからXY相対移動命令列を作る。

        FontStrokeGlyph の各 FontStrokePath は、一回ペンを下ろして書く単位である。
        A の横棒のように一筆書きできない部分は、別 path として扱う。
        """
        commands: List[FontMotionCommand] = []

        current_point = FontPoint(
            x=0.0,
            y=0.0,
        )

        for stroke_path in stroke_glyph:
            if len(stroke_path) == 0:
                continue

            start_point = stroke_path.points[0]

            move_to_start = FontMotionCommand(
                pen=0.0,
                dx=start_point.x - current_point.x,
                dy=start_point.y - current_point.y,
            )
            commands.append(move_to_start)

            current_point = start_point

            pen_down = FontMotionCommand(
                pen=1.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_down)

            for point_index in range(1, len(stroke_path.points)):
                next_point = stroke_path.points[point_index]

                command = FontMotionCommand(
                    pen=1.0,
                    dx=next_point.x - current_point.x,
                    dy=next_point.y - current_point.y,
                )
                commands.append(command)

                current_point = next_point

            pen_up = FontMotionCommand(
                pen=0.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_up)

        return commands

    def rebuild_centerline(
        self,
        commands: List[FontMotionCommand],
        text: str,
    ) -> FontCenterlineGlyph:
        """XY相対移動命令列を中心線データへ戻す。"""
        paths: List[FontCenterlinePath] = []
        current_points: List[FontPoint] = []

        current_point = FontPoint(
            x=0.0,
            y=0.0,
        )

        pen_is_down = False

        for command in commands:
            current_point = FontPoint(
                x=current_point.x + command.dx,
                y=current_point.y + command.dy,
            )

            if command.pen == 0.0:
                if pen_is_down:
                    if len(current_points) > 0:
                        paths.append(
                            FontCenterlinePath(
                                points=current_points,
                            )
                        )

                    current_points = []

                pen_is_down = False

            if command.pen != 0.0:
                if pen_is_down is False:
                    current_points = [
                        current_point,
                    ]
                    pen_is_down = True

                else:
                    current_points.append(current_point)

        if len(current_points) > 0:
            paths.append(
                FontCenterlinePath(
                    points=current_points,
                )
            )

        return FontCenterlineGlyph(
            text=text,
            paths=paths,
        )


def main() -> None:
    """筆順付き stroke からXY相対移動命令を作る処理を単体確認する。"""
    from font_alphabet_stroke_builder import FontAlphabetStrokeBuilder

    stroke_builder = FontAlphabetStrokeBuilder(
        height=40.0,
        spacing=5.0,
    )

    stroke_glyph = stroke_builder.build_text(
        text="A",
    )

    builder = FontMotionBuilder()

    commands = builder.build_from_stroke(
        stroke_glyph=stroke_glyph,
    )

    for command in commands:
        print(command)


if __name__ == "__main__":
    main()
