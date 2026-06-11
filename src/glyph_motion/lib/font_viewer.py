#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

フォント処理の各段階を画面表示する。

このモジュールは、次の4段階を目視確認するための表示クラスを定義する。

1. FontOutlineGlyph
   フォントから取得した輪郭線を線として表示する。

2. FontFilledGlyph
   輪郭を塗りつぶして得た文字領域を画像として表示する。

3. FontCenterlineGlyph
   文字領域から抽出した中心線を線として表示する。

4. FontStrokeGlyph
   筆順付きの stroke を線として表示する。

このモジュールは表示だけを担当する。
フォント読み込み、輪郭抽出、塗りつぶし、中心線抽出、筆順生成、移動命令生成は行わない。
"""

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from glyph_motion.lib.font_geometry import FontCenterlineGlyph
from glyph_motion.lib.font_geometry import FontFilledGlyph
from glyph_motion.lib.font_geometry import FontOutlineGlyph
from glyph_motion.lib.font_geometry import FontStrokeGlyph


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

    def show_stroke(
        self,
        stroke_glyph: FontStrokeGlyph,
    ) -> None:
        """筆順付き stroke を線として表示する。

        FontStrokeGlyph の paths の順序は、ロボットが実際に書く順序である。
        各 FontStrokePath は、一回ペンを下ろして書く単位である。
        """
        plt.figure()

        for path_index, path in enumerate(stroke_glyph):
            x_values: List[float] = []
            y_values: List[float] = []

            for point in path:
                x_values.append(point.x)
                y_values.append(point.y)

            plt.plot(
                x_values,
                y_values,
                marker=".",
                label="stroke {}".format(path_index + 1),
            )

            if len(path) > 0:
                start_point = path.points[0]
                plt.text(
                    start_point.x,
                    start_point.y,
                    str(path_index + 1),
                )

        plt.legend()

        self._finish_plot(
            title="stroke: {}".format(stroke_glyph.text),
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
    from font_alphabet_stroke_builder import FontAlphabetStrokeBuilder

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


if __name__ == "__main__":
    main()
