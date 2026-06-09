from typing import List

import matplotlib.pyplot as plt

from font_geometry import GlyphMesh
from font_geometry import MeshPath
from font_geometry import MeshPoint


class FontMeshViewer:
    """GlyphMeshを画面表示するクラスである。"""

    def show_points(
        self,
        glyph_mesh: GlyphMesh,
        point_size: float = 4.0,
    ) -> None:
        """GlyphMeshを点として表示する。"""
        plt.figure()

        for mesh_path in glyph_mesh:
            x_values: List[float] = []
            y_values: List[float] = []

            for point in mesh_path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.scatter(
                x_values,
                y_values,
                s=point_size,
            )

        plt.gca().set_aspect(
            "equal",
            adjustable="box",
        )
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()

    def show_lines(
        self,
        glyph_mesh: GlyphMesh,
    ) -> None:
        """GlyphMeshを線で表示する。"""
        plt.figure()

        for mesh_path in glyph_mesh:
            x_values: List[float] = []
            y_values: List[float] = []

            for point in mesh_path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.plot(
                x_values,
                y_values,
                marker=".",
            )

        plt.gca().set_aspect(
            "equal",
            adjustable="box",
        )
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()


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

    viewer = FontMeshViewer()
    viewer.show_lines(
        glyph_mesh=glyph_mesh,
    )


if __name__ == "__main__":
    main()