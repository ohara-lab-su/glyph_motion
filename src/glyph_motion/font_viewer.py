"""
フォント処理の各段階を画面表示する。

このモジュールは、次の3段階を目視確認するための表示クラスを定義する。

1. FontOutlineGlyph
   フォントから取得した輪郭線を線として表示する。

2. FontFilledGlyph
   輪郭を塗りつぶして得た文字領域を画像として表示する。

3. FontCenterlineGlyph
   文字領域から抽出した中心線を線として表示する。

このモジュールは表示だけを担当する。
フォント読み込み、輪郭抽出、塗りつぶし、中心線抽出、移動命令生成は行わない。
"""

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from font_geometry import FontCenterlineGlyph
from font_geometry import FontFilledGlyph
from font_geometry import FontOutlineGlyph


class FontViewer:
    """フォント処理途中のデータを目視確認するための表示クラスである。"""

    def show_outline(
        self,
        outline_glyph: FontOutlineGlyph,
    ) -> None:
        """フォント輪郭を線として表示する。

        FontOutlineGlyph が文字の輪郭として成立しているかを確認する。
        """
        plt.figure()

        for path in outline_glyph:
            x_values: List[float] = []
            y_values: List[float] = []

            for point in path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.plot(
                x_values,
                y_values,
                marker=".",
            )

        self._finish_plot(
            title="outline: {}".format(outline_glyph.text),
        )

    def show_filled(
        self,
        filled_glyph: FontFilledGlyph,
    ) -> None:
        """塗りつぶし済み文字領域を画像として表示する。

        FontFilledGlyph が太さを持つ文字領域として成立しているかを確認する。
        """
        plt.figure()

        image = np.flipud(filled_glyph.mask)

        plt.imshow(
            image,
            interpolation="nearest",
            extent=self._make_extent(filled_glyph),
        )

        self._finish_plot(
            title="filled: {}".format(filled_glyph.text),
        )

    def show_centerline(
        self,
        centerline_glyph: FontCenterlineGlyph,
    ) -> None:
        """中心線を線として表示する。

        FontCenterlineGlyph がロボットでなぞる線として成立しているかを確認する。
        """
        plt.figure()

        for path in centerline_glyph:
            x_values: List[float] = []
            y_values: List[float] = []

            for point in path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.plot(
                x_values,
                y_values,
                marker=".",
            )

        self._finish_plot(
            title="centerline: {}".format(centerline_glyph.text),
        )

    def show_filled_with_centerline(
        self,
        filled_glyph: FontFilledGlyph,
        centerline_glyph: FontCenterlineGlyph,
    ) -> None:
        """塗りつぶし領域と中心線を重ねて表示する。

        中心線が文字領域の中央付近を通っているかを確認する。
        """
        plt.figure()

        image = np.flipud(filled_glyph.mask)

        plt.imshow(
            image,
            interpolation="nearest",
            extent=self._make_extent(filled_glyph),
        )

        for path in centerline_glyph:
            x_values: List[float] = []
            y_values: List[float] = []

            for point in path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.plot(
                x_values,
                y_values,
                marker=".",
            )

        self._finish_plot(
            title="filled + centerline: {}".format(filled_glyph.text),
        )

    def _make_extent(
        self,
        filled_glyph: FontFilledGlyph,
    ) -> List[float]:
        """imshow用の表示範囲を作る。"""
        row_count = filled_glyph.mask.shape[0]
        column_count = filled_glyph.mask.shape[1]

        x_min = filled_glyph.x_min
        x_max = filled_glyph.x_min + float(column_count) * filled_glyph.pixel_size

        y_min = filled_glyph.y_min
        y_max = filled_glyph.y_min + float(row_count) * filled_glyph.pixel_size

        return [
            x_min,
            x_max,
            y_min,
            y_max,
        ]

    def _finish_plot(
        self,
        title: str,
    ) -> None:
        """表示用の共通設定を行う。"""
        plt.title(title)
        plt.gca().set_aspect(
            "equal",
            adjustable="box",
        )
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()


def main() -> None:
    """FontViewerの表示機能を単体確認する。"""
    from pathlib import Path

    from font_centerline_cleaner import FontCenterlineCleaner
    from font_centerline_extractor import FontCenterlineExtractor
    from font_fill_glyph import FontGlyphFiller
    from font_outline_extractor import FontOutlineExtractor

    # font_file = Path("NotoSansCJKjp-Regular.otf")
    font_file = Path("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc")

    if font_file.exists() is False:
        print(f"{font_file} が見つからない。")
        return

    extractor = FontOutlineExtractor(
        font_file=font_file,
        height=40.0,
        curve_division=8,
        font_number=0,
    )

    outline = extractor.extract_text(
        text="A",
        spacing=5.0,
    )

    filler = FontGlyphFiller(
        pixel_size=0.5,
        margin=2.0,
    )

    filled = filler.fill(
        outline_glyph=outline,
    )

    # --------------- 基本テスト
    # viewer = FontViewer()
    # アウトラインフォント表示
    # viewer.show_outline(outline)
    # ２値化して埋める
    # viewer.show_filled(filled)

    # --------------- 中心線取り出して表示
    centerline_extractor = FontCenterlineExtractor()

    raw_centerline = centerline_extractor.extract(
        filled_glyph=filled,
    )

    centerline_cleaner = FontCenterlineCleaner(
        min_path_length=1.0,
        point_spacing=1.0,
    )

    centerline = centerline_cleaner.clean(
        centerline_glyph=raw_centerline,
    )

    viewer = FontViewer()

    viewer.show_outline(
        outline_glyph=outline,
    )

    viewer.show_filled(
        filled_glyph=filled,
    )

    viewer.show_centerline(
        centerline_glyph=centerline,
    )

    viewer.show_filled_with_centerline(
        filled_glyph=filled,
        centerline_glyph=centerline,
    )


if __name__ == "__main__":
    main()
