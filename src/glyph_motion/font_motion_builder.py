"""
中心線データをXY相対移動命令へ変換する。

このモジュールは FontCenterlineGlyph を入力として受け取り、
FontMotionCommand の列を出力する。

入力される FontCenterlineGlyph は、FontCenterlineCleaner で整理済みの
中心線であることを前提にする。

FontCenterlineCleaner を外から渡した場合は、このクラス内部で中心線整理を
行ってから相対移動命令を作る。

このモジュールでは、ロボット固有APIは呼ばない。
ここで作るのは、既存のロボット制御プログラムへ渡す前段の
抽象的なXY相対移動命令である。
"""

from typing import List
from typing import Optional

from font_centerline_cleaner import FontCenterlineCleaner
from font_geometry import FontCenterlineGlyph
from font_geometry import FontCenterlinePath
from font_geometry import FontMotionCommand
from font_geometry import FontPoint


class FontMotionBuilder:
    """中心線をXY相対移動命令列へ変換するクラスである。"""

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
    """中心線整理とXY相対移動命令化を単体確認する。"""
    from font_geometry import FontCenterlineGlyph
    from font_geometry import FontCenterlinePath
    from font_viewer import FontViewer

    centerline = FontCenterlineGlyph(
        text="test",
        paths=[
            FontCenterlinePath(
                points=[
                    FontPoint(x=0.0, y=0.0),
                    FontPoint(x=0.0, y=0.0),
                    FontPoint(x=10.0, y=0.0),
                    FontPoint(x=10.0, y=10.0),
                ],
            ),
        ],
    )

    cleaner = FontCenterlineCleaner(
        min_path_length=1.0,
        point_spacing=2.0,
    )

    builder = FontMotionBuilder(
        centerline_cleaner=cleaner,
    )

    commands = builder.build(
        centerline_glyph=centerline,
    )

    for command in commands:
        print(command)

    rebuilt_centerline = builder.rebuild_centerline(
        commands=commands,
        text=centerline.text,
    )

    viewer = FontViewer()
    viewer.show_centerline(
        centerline_glyph=rebuilt_centerline,
    )


if __name__ == "__main__":
    main()