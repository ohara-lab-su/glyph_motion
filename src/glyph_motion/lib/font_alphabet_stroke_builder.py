#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

アルファベット文字列から筆順付き stroke データを生成する。

このモジュールは、通常フォントのアウトラインを使わない。
最初からロボットでなぞるための single-line stroke を生成する。

既存のアウトラインフォント処理とは別系統の入力経路である。
既存の outline -> filled -> centerline -> motion の処理はそのまま残す。

このモジュールが出力する FontStrokeGlyph は、筆順を持つ。
FontStrokeGlyph の各 FontStrokePath は、一回ペンを下ろして書く単位である。

stroke 内部は、粗い制御点をそのまま直線で結ぶだけではなく、
stroke_division に従って細かい点列へ分割する。

これにより、FontMotionBuilder は変更せずに、
より細かいロボット移動命令を生成できる。
"""

from typing import Dict, List, Tuple

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokeGlyph
from glyph_motion.lib.font_geometry import FontStrokePath


RawStroke = List[Tuple[float, float]]
RawGlyph = List[RawStroke]


class FontAlphabetStrokeBuilder:
    """アルファベット文字列から筆順付き stroke データを作るクラスである。"""

    def __init__(
        self,
        height: float,
        spacing: float,
        stroke_division: int = 20,
    ) -> None:
        """文字高さ、文字間隔、stroke内分割数を設定する。"""
        if height <= 0.0:
            raise ValueError("height は正の値である必要がある。")

        if spacing < 0.0:
            raise ValueError("spacing は0以上である必要がある。")

        if stroke_division < 1:
            raise ValueError("stroke_division は1以上である必要がある。")

        self._height = height
        self._spacing = spacing
        self._stroke_division = stroke_division
        self._width = height * 0.7
        self._glyphs = self._build_glyph_table()

    def build_text(
        self,
        text: str,
    ) -> FontStrokeGlyph:
        """文字列を筆順付き stroke データへ変換する。"""
        stroke_paths: List[FontStrokePath] = []
        x_offset = 0.0

        for character in text:
            upper_character = character.upper()

            if upper_character == " ":
                x_offset = x_offset + self._width + self._spacing
                continue

            if upper_character not in self._glyphs:
                raise ValueError("未定義の文字である: {}".format(character))

            raw_glyph = self._glyphs[upper_character]

            for raw_stroke in raw_glyph:
                normalized_points = self._subdivide_raw_stroke(
                    raw_stroke=raw_stroke,
                )

                points: List[FontPoint] = []

                for raw_point in normalized_points:
                    points.append(
                        FontPoint(
                            x=x_offset + raw_point[0] * self._width,
                            y=raw_point[1] * self._height,
                        )
                    )

                stroke_paths.append(
                    FontStrokePath(
                        points=points,
                    )
                )

            x_offset = x_offset + self._width + self._spacing

        return FontStrokeGlyph(
            text=text,
            paths=stroke_paths,
        )

    def _subdivide_raw_stroke(
        self,
        raw_stroke: RawStroke,
    ) -> RawStroke:
        """stroke 内の各線分を細かい点列へ分割する。"""
        if len(raw_stroke) < 2:
            return raw_stroke

        points: RawStroke = [
            raw_stroke[0],
        ]

        for point_index in range(1, len(raw_stroke)):
            start_point = raw_stroke[point_index - 1]
            end_point = raw_stroke[point_index]

            segment_points = self._subdivide_segment(
                start_point=start_point,
                end_point=end_point,
            )

            for segment_point in segment_points:
                points.append(segment_point)

        return points

    def _subdivide_segment(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
    ) -> RawStroke:
        """2点間の線分を stroke_division 個の小区間へ分割する。

        返す点列には始点を含めない。
        終点は含める。
        """
        points: RawStroke = []

        start_x = start_point[0]
        start_y = start_point[1]
        end_x = end_point[0]
        end_y = end_point[1]

        for division_index in range(1, self._stroke_division + 1):
            ratio = float(division_index) / float(self._stroke_division)

            x = start_x + (end_x - start_x) * ratio
            y = start_y + (end_y - start_y) * ratio

            points.append(
                (
                    x,
                    y,
                )
            )

        return points

    def _build_glyph_table(self) -> Dict[str, RawGlyph]:
        """内蔵 stroke 定義を返す。

        座標は 0.0 から 1.0 の正規化座標で定義する。
        path の順序が筆順である。

        ここで定義する点は制御点に近い粗い点である。
        実際に返す FontStrokeGlyph では、stroke_division に従って
        各線分を細かい点列へ分割する。
        """
        glyphs: Dict[str, RawGlyph] = {}

        glyphs["A"] = [
            [(0.0, 0.0), (0.5, 1.0)],
            [(0.5, 1.0), (1.0, 0.0)],
            [(0.25, 0.45), (0.75, 0.45)],
        ]

        glyphs["B"] = [
            [(0.0, 0.0), (0.0, 1.0)],
            [(0.0, 1.0), (0.65, 0.85), (0.65, 0.55), (0.0, 0.5)],
            [(0.0, 0.5), (0.75, 0.4), (0.75, 0.1), (0.0, 0.0)],
        ]

        glyphs["C"] = [
            [(0.8, 0.9), (0.2, 0.9), (0.0, 0.5), (0.2, 0.1), (0.8, 0.1)],
        ]

        glyphs["I"] = [
            [(0.2, 1.0), (0.8, 1.0)],
            [(0.5, 1.0), (0.5, 0.0)],
            [(0.2, 0.0), (0.8, 0.0)],
        ]

        glyphs["L"] = [
            [(0.0, 1.0), (0.0, 0.0), (0.8, 0.0)],
        ]

        glyphs["O"] = [
            [
                (0.5, 1.0),
                (0.1, 0.8),
                (0.1, 0.2),
                (0.5, 0.0),
                (0.9, 0.2),
                (0.9, 0.8),
                (0.5, 1.0),
            ],
        ]

        glyphs["T"] = [
            [(0.0, 1.0), (1.0, 1.0)],
            [(0.5, 1.0), (0.5, 0.0)],
        ]

        glyphs["X"] = [
            [(0.0, 1.0), (1.0, 0.0)],
            [(1.0, 1.0), (0.0, 0.0)],
        ]

        glyphs["Y"] = [
            [(0.0, 1.0), (0.5, 0.55), (1.0, 1.0)],
            [(0.5, 0.55), (0.5, 0.0)],
        ]

        glyphs["Z"] = [
            [(0.0, 1.0), (1.0, 1.0), (0.0, 0.0), (1.0, 0.0)],
        ]

        return glyphs


def main() -> None:
    """アルファベット stroke 生成を単体確認する。"""
    from font_viewer import FontViewer

    builder = FontAlphabetStrokeBuilder(
        height=40.0,
        spacing=5.0,
        stroke_division=20,
    )

    stroke_glyph = builder.build_text(
        text="A",
    )

    print(stroke_glyph)

    viewer = FontViewer()
    viewer.show_stroke(
        stroke_glyph=stroke_glyph,
    )


if __name__ == "__main__":
    main()
