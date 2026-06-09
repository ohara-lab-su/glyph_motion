from typing import List

from font_geometry import GlyphMesh, MeshPath, MeshPoint


class FontRasterizer:
    """GlyphMeshの各線分を指定された一定間隔の点列へ再分割（再サンプリング）するクラスである。"""

    def __init__(self, step: float) -> None:
        """指定されたサンプリングステップ幅でインスタンスを初期化する。

        Args:
            step (float): サンプリングを行う際の長さの増分値。

        Raises:
            ValueError: stepが0以下の場合に送出される。
        """
        if step <= 0.0:
            raise ValueError("step は正の値である必要がある。")
        self._step = step

    def rasterize(self, glyph_mesh: GlyphMesh) -> GlyphMesh:
        """入力されたGlyphMeshの全パスに対して再分割処理を一括適用する。

        Args:
            glyph_mesh (GlyphMesh): 再サンプリング対象の幾何メッシュ。

        Returns:
            GlyphMesh: 指定ステップで等間隔化された点列を持つ新しいGlyphMesh。
        """
        rasterized_paths: List[MeshPath] = []
        for mesh_path in glyph_mesh:
            rasterized_paths.append(self._rasterize_path(mesh_path=mesh_path))
        return GlyphMesh(paths=rasterized_paths)

    def _rasterize_path(self, mesh_path: MeshPath) -> MeshPath:
        """単一のMeshPathオブジェクト内の線分要素を指定間隔へ再分割する。

        Args:
            mesh_path (MeshPath): 変換対象のパス。

        Returns:
            MeshPath: 再サンプリング済みの新しいパス。
        """
        rasterized_points: List[MeshPoint] = []

        if len(mesh_path) == 0:
            return MeshPath(
                points=rasterized_points,
                closed=mesh_path.closed,
            )

        rasterized_points.append(mesh_path.points[0])

        for point_index in range(1, len(mesh_path.points)):
            start_point = mesh_path.points[point_index - 1]
            end_point = mesh_path.points[point_index]

            line_points = self._rasterize_line(
                start_point=start_point,
                end_point=end_point,
            )
            for line_point in line_points:
                rasterized_points.append(line_point)

        return MeshPath(
            points=rasterized_points,
            closed=mesh_path.closed,
        )

    def _rasterize_line(
        self, start_point: MeshPoint, end_point: MeshPoint
    ) -> List[MeshPoint]:
        """2点間を結ぶ直線セグメントを、指定された距離ステップに基づいて分割した点列を作る。

        Args:
            start_point (MeshPoint): 線分の開始点。
            end_point (MeshPoint): 線分の終了点。

        Returns:
            List[MeshPoint]: 分割点のリスト（開始点は含まれず、終了点は含まれる）。
        """
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance == 0.0:
            return []

        division_count = int(distance / self._step)
        if division_count < 1:
            division_count = 1

        points: List[MeshPoint] = []
        for division_index in range(1, division_count + 1):
            ratio = float(division_index) / float(division_count)
            points.append(
                MeshPoint(
                    x=start_point.x + dx * ratio,
                    y=start_point.y + dy * ratio,
                )
            )
        return points


def main() -> None:
    """単一の直線パスに対して、指定の刻み幅で正しくラスタライズされるかを検証する。"""
    glyph_mesh = GlyphMesh(
        paths=[
            MeshPath(
                points=[
                    MeshPoint(x=0.0, y=0.0),
                    MeshPoint(x=10.0, y=0.0),
                ],
                closed=False,
            ),
        ],
    )

    rasterizer = FontRasterizer(step=1.0)
    rasterized_mesh = rasterizer.rasterize(glyph_mesh=glyph_mesh)
    print(rasterized_mesh)


if __name__ == "__main__":
    main()