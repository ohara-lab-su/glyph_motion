"""
KanjiVG から漢字の筆順付き stroke を読み込み、XY相対移動命令へ変換する確認用スクリプトである。

このスクリプトは、次の流れを確認する。

KanjiVG SVG
->
FontStrokeGlyph
->
FontMotionCommand

ここではロボット固有APIは呼ばない。
生成された FontMotionCommand を表示し、ペンアップ・ペンダウン単位が
stroke ごとに分かれているか確認する。
"""

from pathlib import Path

from font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader
from font_motion_builder import FontMotionBuilder
from font_viewer import FontViewer


def main() -> None:
    """KanjiVG stroke から相対移動命令を生成する。"""
    kanjivg_directory = Path("kanjivg/kanji")

    loader = FontKanjiVGStrokeLoader(
        kanjivg_directory=kanjivg_directory,
        height=40.0,
        spacing=5.0,
        curve_division=20,
    )

    stroke_glyph = loader.load_text(
        text="島",
    )

    viewer = FontViewer()
    viewer.show_stroke(
        stroke_glyph=stroke_glyph,
    )

    motion_builder = FontMotionBuilder()
    commands = motion_builder.build_from_stroke(
        stroke_glyph=stroke_glyph,
    )

    for command in commands:
        print(command)


if __name__ == "__main__":
    main()
