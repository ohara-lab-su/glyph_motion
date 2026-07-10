#!/usr/bin/env python
""" """

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from glyph_motion.lib.font_viewer import FontViewer


def main() -> None:
    """FontViewerの表示機能を単体確認する。"""
    from font_alphabet_stroke_builder import FontAlphabetStrokeBuilder

    # アルファベット用ストローク作成
    stroke_builder = FontAlphabetStrokeBuilder(
        height=40.0,
        spacing=5.0,
    )

    stroke_glyph = stroke_builder.build_text(
        text="A",
        # text="-",
    )

    viewer = FontViewer()
    viewer.show_stroke(
        stroke_glyph=stroke_glyph,
    )


if __name__ == "__main__":
    main()
