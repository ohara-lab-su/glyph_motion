from dataclasses import dataclass
from typing import List

from font_geometry import GlyphMesh, MeshPath, MeshPoint


@dataclass
class MotionCommand:
    """ロボットの座標差分による物理的な駆動・移動制御命令を表すデータクラスである。

    pen値が1.0の時は描画状態（接地移動）、0.0の時は非描画移動（空送り移動）を示す。
    """

    pen: float
    dx: float
    dy: float


class RobotMotionBuilder:
    """GlyphMeshの幾何データを、ロボットプロッター向けの相対移動命令列へ相互変換するクラスである。"""

    def build_relative_motion(self, glyph_mesh: GlyphMesh) -> List[MotionCommand]:
        """入力されたGlyphMeshから物理駆動用の相対移動命令列を組み立てる。

        Args:
            glyph_mesh (GlyphMesh): 変換元の幾何メッシュデータ。

        Returns:
            List[MotionCommand]: 再構築された制御シークエンスコマンドリスト。
        """
        commands: List[MotionCommand] = []
        current_x = 0.0
        current_y = 0.0

        for mesh_path in glyph_mesh:
            if len(mesh_path) == 0:
                continue

            start_point = mesh_path.points[0]

            # 始点への空送り移動
            move_to_start = MotionCommand(
                pen=0.0,
                dx=start_point.x - current_x,
                dy=start_point.y - current_y,
            )
            commands.append(move_to_start)

            current_x = start_point.x
            current_y = start_point.y

            # 描画状態への切り替え
            pen_down = MotionCommand(pen=1.0, dx=0.0, dy=0.0)
            commands.append(pen_down)

            # パスに沿った連続移動命令の付加
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

            # 筆記の終了にともなう非描画状態へのリセット
            pen_up = MotionCommand(pen=0.0, dx=0.0, dy=0.0)
            commands.append(pen_up)

        return commands

    def rebuild_glyph_mesh(self, commands: List[MotionCommand]) -> GlyphMesh:
        """相対移動命令のシーケンスを逆算解析し、元の幾何学的なGlyphMesh構造体を復元する。

        Args:
            commands (List[MotionCommand]): ロボット指令制御コマンド配列。

        Returns:
            GlyphMesh: 累積座標から再構成された図形メッシュデータ。
        """
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
                        mesh_path = MeshPath(points=current_points, closed=False)
                        paths.append(mesh_path)
                    current_points = []
                pen_is_down = False

            if command.pen != 0.0:
                point = MeshPoint(x=current_x, y=current_y)
                if pen_is_down is False:
                    current_points = [point]
                    pen_is_down = True
                else:
                    current_points.append(point)

        if len(current_points) > 0:
            mesh_path = MeshPath(points=current_points, closed=False)
            paths.append(mesh_path)

        return GlyphMesh(paths=paths)


def main() -> None:
    """一連の閉じた矩形図形に対して命令の相互変換および復元処理が同一性を保持するか検証する。"""
    glyph_mesh = GlyphMesh(
        paths=[
            MeshPath(
                points=[
                    MeshPoint(x=0.0, y=0.0),
                    MeshPoint(x=10.0, y=0.0),
                    MeshPoint(x=10.0, y=10.0),
                    MeshPoint(x=0.0, y=10.0),
                    MeshPoint(x=0.0, y=0.0),
                ],
                closed=True,
            ),
        ],
    )

    builder = RobotMotionBuilder()
    commands = builder.build_relative_motion(glyph_mesh=glyph_mesh)

    for command in commands:
        print(command)

    rebuilt_mesh = builder.rebuild_glyph_mesh(commands=commands)
    print(rebuilt_mesh)


if __name__ == "__main__":
    main()