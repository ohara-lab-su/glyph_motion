from typing import List
import matplotlib.pyplot as plt
from font_geometry import GlyphMesh


class FontMeshViewer:
    """GlyphMeshを画面表示するクラスである。"""

    def show_points(self, glyph_mesh: GlyphMesh, point_size: float = 4.0) -> None:
        """GlyphMeshを点として表示する。"""
        plt.figure()
        for mesh_path in glyph_mesh:
            x_values: List[float] = []
            y_values: List[float] = []
            for point in mesh_path:
                x_values.append(point.x)
                y_values.append(point.y)
            plt.scatter(x_values, y_values, s=point_size)
        self._finish_plot()

    def show_lines(self, glyph_mesh: GlyphMesh) -> None:
        """GlyphMeshを線で表示する。"""
        plt.figure()
        for mesh_path in glyph_mesh:
            x_values: List[float] = []
            y_values: List[float] = []
            for point in mesh_path:
                x_values.append(point.x)
                y_values.append(point.y)
            plt.plot(x_values, y_values, marker=".")
        self._finish_plot()

    def _finish_plot(self) -> None:
        """表示用の共通設定を行う。"""
        plt.gca().set_aspect("equal", adjustable="box")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()