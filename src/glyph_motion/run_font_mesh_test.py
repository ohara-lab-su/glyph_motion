from pathlib import Path

from font_glyph_mesh import FontGlyphMesh
from font_mesh_viewer import FontMeshViewer
from font_rasterizer import FontRasterizer


def main() -> None:
    font_file = Path("NotoSansCJKjp-Regular.otf")

    if font_file.exists() is False:
        print("NotoSansCJKjp-Regular.otf が見つからない。")
        return

    font_glyph_mesh = FontGlyphMesh(
        font_file=font_file,
        height=40.0,
        curve_division=8,
    )

    glyph_mesh = font_glyph_mesh.get_text_mesh(
        text="島",
        spacing=5.0,
    )

    viewer = FontMeshViewer()

    viewer.show_lines(
        glyph_mesh=glyph_mesh,
    )

    rasterizer = FontRasterizer(
        step=0.5,
    )

    rasterized_mesh = rasterizer.rasterize(
        glyph_mesh=glyph_mesh,
    )

    viewer.show_points(
        glyph_mesh=rasterized_mesh,
        point_size=4.0,
    )


if __name__ == "__main__":
    main()