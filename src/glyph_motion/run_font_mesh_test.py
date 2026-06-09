from pathlib import Path

from fong_glyph_mesh import FontGlyphMesh
from font_mesh_viewer import FontMeshViewer
from font_rasterizer import FontRasterizer


def main() -> None:
    font_file = Path("NotoSansCJKjp-Regular.otf")

    if not font_file.exists():
        raise FileNotFoundError(
            "NotoSansCJKjp-Regular.otf が見つからない。"
        )

    font_mesh = FontGlyphMesh(
        font_file=font_file,
        height_mm=40.0,
        curve_division=8,
    )

    glyph_mesh = font_mesh.get_text_mesh(
        text="島",
        spacing_mm=5.0,
    )

    viewer = FontMeshViewer()
    viewer.show_lines(glyph_mesh)

    rasterizer = FontRasterizer(
        step=0.5,
    )

    rasterized_glyph_mesh = rasterizer.rasterize(glyph_mesh)

    viewer.show_points(
        glyph_mesh=rasterized_glyph_mesh,
        point_size=4.0,
    )


if __name__ == "__main__":
    main()