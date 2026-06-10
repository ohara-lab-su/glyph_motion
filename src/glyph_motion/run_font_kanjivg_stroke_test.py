"""
KanjiVG から漢字の筆順付き stroke を読み込み、表示する確認用スクリプトである。

このスクリプトは、KanjiVG SVG -> FontStrokeGlyph の確認に使う。
モーション命令生成までは行わない。

事前に次のような配置で KanjiVG SVG を置く。

kanjivg/kanji/05cf6.svg

05cf6.svg は「島」に対応する KanjiVG ファイルである。
"""

from pathlib import Path

from font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader
from font_viewer import FontViewer


def main() -> None:
    """KanjiVG stroke を読み込み、筆順付き stroke として表示する。"""
    # kanjivg_directory = Path("kanjivg/kanji")
    kanjivg_directory = Path(__file__).resolve().parent / "data" / "kanjiVG"

    loader = FontKanjiVGStrokeLoader(
        kanjivg_directory=kanjivg_directory,
        height=40.0,
        spacing=5.0,
        curve_division=20,
    )

    stroke_glyph = loader.load_text(
        text="島",
    )

    print(stroke_glyph)
    print("stroke_count =", len(stroke_glyph))

    viewer = FontViewer()
    viewer.show_stroke(
        stroke_glyph=stroke_glyph,
    )


if __name__ == "__main__":
    main()
