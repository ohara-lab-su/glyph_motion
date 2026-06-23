#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

筆順付きアルファベット stroke からモーション命令を生成する確認用スクリプトである。

このスクリプトは通常フォントを使わない。
FontAlphabetStrokeBuilder が持つ内蔵 stroke 定義を使って、
筆順付き stroke -> 相対移動命令 の流れを確認する。

既存のアウトラインフォント処理は使わない。
outline -> filled -> centerline -> motion の経路は、既存機能として別に残す。
"""

from glyph_motion.lib.font_alphabet_stroke_builder import FontAlphabetStrokeBuilder
from glyph_motion.lib.font_viewer import FontViewer
from glyph_motion.font_motion_builder import FontMotionBuilder


def main() -> None:
    """A のような一筆書きできない文字を stroke 単位で確認する。"""
    stroke_builder = FontAlphabetStrokeBuilder(
        height=40.0,
        spacing=5.0,
    )

    stroke_glyph = stroke_builder.build_text(
        # text="A",
        text="B",
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
