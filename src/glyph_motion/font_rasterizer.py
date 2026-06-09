#!/usr/bin/env python
from typing import List

from font_geometry import GlyphMesh
from font_geometry import MeshPath
from font_geometry import MeshPoint


class FontRasterizer:
    """GlyphMeshの各線分を指定間隔の点列へ再分割するクラスである。"""

    def __init__(
        self,
        step: float,
    ) -> None:
        self._step = step

    def rasterize(
        self,
        glyph_mesh: GlyphMesh,
    ) -> GlyphMesh:
        """GlyphMeshを指定間隔の点列へ再分割する。"""
        rasterized_paths: List[MeshPath] = []

        for mesh_path in glyph_mesh:
            rasterized_path = self._rasterize_path(
                mesh_path=mesh_path,
            )
            rasterized_paths.append(rasterized_path)

        return GlyphMesh(
            paths=rasterized_paths,
        )

    def _rasterize_path(
        self,
        mesh_path: MeshPath,
    ) -> MeshPath:
        """1本のMeshPathを指定間隔の点列へ再分割する。"""
        rasterized_points: List[MeshPoint] = []

        if len(mesh_path) == 0:
            return MeshPath(
                points=rasterized_points,
                closed=mesh_path.closed,
            )

        first_point = mesh_path.points[0]
        rasterized_points.append(first_point)

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
        self,
        start_point: MeshPoint,
        end_point: MeshPoint,
    ) -> List[MeshPoint]:
        """線分を指定間隔の点列へ分割する。"""
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

            x = start_point.x + dx * ratio
            y = start_point.y + dy * ratio

            point = MeshPoint(
                x=x,
                y=y,
            )
            points.append(point)

        return points


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
                ],
                closed=False,
            ),
        ],
    )

    rasterizer = FontRasterizer(
        step=1.0,
    )

    rasterized_mesh = rasterizer.rasterize(
        glyph_mesh=glyph_mesh,
    )

    print(rasterized_mesh)


if __name__ == "__main__":
    main()