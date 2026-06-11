#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

フォント輪郭を格子上の塗りつぶし領域へ変換する。

このモジュールは FontOutlineGlyph を入力し、
FontFilledGlyph を出力する。

中心線抽出は行わない。
表示も行わない。
"""

from typing import List

import numpy as np
from matplotlib.path import Path as MatplotlibPath

from glyph_motion.lib.font_geometry import FontFilledGlyph
from glyph_motion.lib.font_geometry import FontOutlineGlyph


class FontGlyphFiller:
    """フォント輪郭を二値の文字領域へ変換する。"""

    def __init__(
        self,
        pixel_size: float,
        margin: float,
    ) -> None:
        """格子間隔と余白を設定する。"""
        if pixel_size <= 0.0:
            raise ValueError("pixel_size は正の値である必要がある。")

        if margin < 0.0:
            raise ValueError("margin は0以上である必要がある。")

        self._pixel_size = pixel_size
        self._margin = margin

    def fill(
        self,
        outline_glyph: FontOutlineGlyph,
    ) -> FontFilledGlyph:
        """輪郭の内側を格子上に塗りつぶす。"""
        x_values: List[float] = []
        y_values: List[float] = []

        for path in outline_glyph:
            for point in path:
                x_values.append(point.x)
                y_values.append(point.y)

        if len(x_values) == 0:
            raise ValueError("輪郭点が存在しない。")

        x_min = min(x_values) - self._margin
        x_max = max(x_values) + self._margin
        y_min = min(y_values) - self._margin
        y_max = max(y_values) + self._margin

        column_count = int(np.ceil((x_max - x_min) / self._pixel_size)) + 1
        row_count = int(np.ceil((y_max - y_min) / self._pixel_size)) + 1

        x_coordinates = x_min + np.arange(column_count) * self._pixel_size
        y_coordinates = y_min + np.arange(row_count) * self._pixel_size

        grid_x, grid_y = np.meshgrid(x_coordinates, y_coordinates)
        sample_points = np.column_stack(
            [
                grid_x.ravel(),
                grid_y.ravel(),
            ]
        )

        mask = np.zeros(
            shape=(row_count, column_count),
            dtype=bool,
        )

        for path in outline_glyph:
            if len(path) < 3:
                continue

            vertices = []

            for point in path:
                vertices.append(
                    (
                        point.x,
                        point.y,
                    )
                )

            matplotlib_path = MatplotlibPath(vertices)
            inside = matplotlib_path.contains_points(sample_points)
            path_mask = inside.reshape(row_count, column_count)

            mask = np.logical_xor(mask, path_mask)

        return FontFilledGlyph(
            text=outline_glyph.text,
            mask=mask,
            x_min=x_min,
            y_min=y_min,
            pixel_size=self._pixel_size,
        )


def main() -> None:
    """塗りつぶし処理を単体確認する。"""
    from pathlib import Path

    from font_outline_extractor import FontOutlineExtractor

    font_file = Path("NotoSansCJKjp-Regular.otf")

    if font_file.exists() is False:
        print("NotoSansCJKjp-Regular.otf が見つからない。")
        return

    extractor = FontOutlineExtractor(
        font_file=font_file,
        height=40.0,
        curve_division=8,
    )

    outline = extractor.extract_text(
        text="島",
        spacing=5.0,
    )

    filler = FontGlyphFiller(
        pixel_size=0.5,
        margin=2.0,
    )

    filled = filler.fill(outline_glyph=outline)

    print(filled.mask.shape)
    print(filled.mask.sum())


if __name__ == "__main__":
    main()
