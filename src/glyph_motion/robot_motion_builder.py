from dataclasses import dataclass
from typing import List

from font_geometry import GlyphMesh
from font_geometry import MeshPath
from font_geometry import MeshPoint


@dataclass
class MotionCommand:
    """座標差分による移動命令を表すデータである。"""

    pen: float
    dx: float
    dy: float


class RobotMotionBuilder:
    """GlyphMeshを相対移動命令列へ変換するクラスである。"""

    def build_relative_motion(
        self,
        glyph_mesh: GlyphMesh,
    ) -> List[MotionCommand]:
        """GlyphMeshから相対移動命令列を作る。"""
        commands: List[MotionCommand] = []

        current_x = 0.0
        current_y = 0.0

        for mesh_path in glyph_mesh:
            if len(mesh_path) == 0:
                continue

            start_point = mesh_path.points[0]

            move_to_start = MotionCommand(
                pen=0.0,
                dx=start_point.x - current_x,
                dy=start_point.y - current_y,
            )
            commands.append(move_to_start)

            current_x = start_point.x
            current_y = start_point.y

            pen_down = MotionCommand(
                pen=1.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_down)

            for point_index in range(1, len(mesh_path.points)):
                point = mesh_path.points[point_index]

                command = MotionCommand(
                    pen=1.0,
                    dx=point.x - current_x,
                    dy=point.y - current_y,
                )
                commands.append(command)

                current_x = point.x
                current_y = point.y

            pen_up = MotionCommand(
                pen=0.0,
                dx=0.0,
                dy=0.0,
            )
            commands.append(pen_up)

        return commands

    def rebuild_glyph_mesh(
        self,
        commands: List[MotionCommand],
    ) -> GlyphMesh:
        """相対移動命令列からGlyphMeshを復元する。"""
        paths: List[MeshPath] = []
        current_points: List[MeshPoint] = []

        current_x = 0.0
        current_y = 0.0
        pen_is_down = False

        for command in commands:
            current_x = current_x + command.dx
            current_y = current_y + command.dy

            if command.pen == 0.0:
                if pen_is_down:
                    if len(current_points) > 0:
                        mesh_path = MeshPath(
                            points=current_points,
                            closed=False,
                        )
                        paths.append(mesh_path)

                    current_points = []

                pen_is_down = False

            if command.pen != 0.0:
                point = MeshPoint(
                    x=current_x,
                    y=current_y,
                )

                if pen_is_down is False:
                    current_points = [
                        point,
                    ]
                    pen_is_down = True

                else:
                    current_points.append(point)

        if len(current_points) > 0:
            mesh_path = MeshPath(
                points=current_points,
                closed=False,
            )
            paths.append(mesh_path)

        return GlyphMesh(
            paths=paths,
        )


def main() -> None:
    glyph_mesh = GlyphMesh(
        paths=[
            MeshPath(
                points=[
                    MeshPoint(
                        x=0.0,
                        y=0.0,
                    ),
                    MeshPoint(
                        x=10.0,
                        y=0.0,
                    ),
                    MeshPoint(
                        x=10.0,
                        y=10.0,
                    ),
                    MeshPoint(
                        x=0.0,
                        y=10.0,
                    ),
                    MeshPoint(
                        x=0.0,
                        y=0.0,
                    ),
                ],
                closed=True,
            ),
        ],
    )

    builder = RobotMotionBuilder()

    commands = builder.build_relative_motion(
        glyph_mesh=glyph_mesh,
    )

    for command in commands:
        print(command)

    rebuilt_mesh = builder.rebuild_glyph_mesh(
        commands=commands,
    )

    print(rebuilt_mesh)


if __name__ == "__main__":
    main()