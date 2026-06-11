#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

フォントファイルから指定文字列の輪郭を取り出す。

このモジュールは、フォントが持つベクトル輪郭を FontOutlineGlyph へ変換する。
ここでは塗りつぶし、中心線抽出、表示、移動命令生成は行わない。
"""

from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from font_geometry import FontOutlineGlyph
from font_geometry import FontOutlinePath
from font_geometry import FontPoint


class FontOutlineExtractor:
    """フォントファイルから文字輪郭を取り出すクラスである。"""

    def __init__(
        self,
        font_file: Path,
        height: float,
        curve_division: int,
        font_number: int = 0,
    ) -> None:
        """フォントファイルと輪郭点列化条件を設定する。"""
        if height <= 0.0:
            raise ValueError("height は正の値である必要がある。")

        if curve_division < 1:
            raise ValueError("curve_division は1以上である必要がある。")

        self._font_file = font_file
        self._height = height
        self._curve_division = curve_division

        # self._font = TTFont(str(font_file))
        self._font = TTFont(
            str(font_file),
            fontNumber=font_number,
        )

        self._cmap = self._font.getBestCmap()
        self._glyph_set = self._font.getGlyphSet()

        units_per_em = float(self._font["head"].unitsPerEm)
        self._scale = self._height / units_per_em

    def extract_text(
        self,
        text: str,
        spacing: float,
    ) -> FontOutlineGlyph:
        """文字列全体の輪郭群を取得する。"""
        paths: List[FontOutlinePath] = []
        x_offset = 0.0

        for character in text:
            character_glyph = self.extract_character(character)

            for path in character_glyph:
                shifted_points: List[FontPoint] = []

                for point in path:
                    shifted_points.append(
                        FontPoint(
                            x=point.x + x_offset,
                            y=point.y,
                        )
                    )

                paths.append(
                    FontOutlinePath(
                        points=shifted_points,
                        closed=path.closed,
                    )
                )

            glyph_name = self._get_glyph_name(character)
            advance_width = self._font["hmtx"].metrics[glyph_name][0]
            x_offset = x_offset + float(advance_width) * self._scale
            x_offset = x_offset + spacing

        return FontOutlineGlyph(
            text=text,
            paths=paths,
        )

    def extract_character(
        self,
        character: str,
    ) -> FontOutlineGlyph:
        """一文字の輪郭群を取得する。"""
        if len(character) != 1:
            raise ValueError("character は1文字である必要がある。")

        glyph_name = self._get_glyph_name(character)
        glyph = self._glyph_set[glyph_name]

        pen = RecordingPen()
        glyph.draw(pen)

        outline_glyph = self._recording_to_outline_glyph(
            text=character,
            recording=pen.value,
        )

        return self._scale_outline_glyph(outline_glyph)

    def _get_glyph_name(
        self,
        character: str,
    ) -> str:
        """文字に対応するフォント内部グリフ名を返す。"""
        code_point = ord(character)

        if code_point not in self._cmap:
            raise ValueError("フォントに含まれていない文字である。")

        return self._cmap[code_point]

    def _recording_to_outline_glyph(
        self,
        text: str,
        recording: List[Tuple[str, Tuple[Any, ...]]],
    ) -> FontOutlineGlyph:
        """RecordingPenの命令列を輪郭点列へ変換する。"""
        paths: List[FontOutlinePath] = []
        current_points: List[FontPoint] = []
        current_point: Optional[FontPoint] = None
        start_point: Optional[FontPoint] = None

        for command_name, command_args in recording:
            if command_name == "moveTo":
                if len(current_points) > 0:
                    paths.append(
                        FontOutlinePath(
                            points=current_points,
                            closed=False,
                        )
                    )

                raw_point = command_args[0]
                current_point = FontPoint(
                    x=float(raw_point[0]),
                    y=float(raw_point[1]),
                )
                start_point = current_point
                current_points = [current_point]

            elif command_name == "lineTo":
                raw_point = command_args[0]
                current_point = FontPoint(
                    x=float(raw_point[0]),
                    y=float(raw_point[1]),
                )
                current_points.append(current_point)

            elif command_name == "qCurveTo":
                if current_point is not None:
                    curve_points = self._qcurve_to_points(
                        current_point=current_point,
                        command_args=command_args,
                    )

                    for point in curve_points:
                        current_points.append(point)

                    if len(curve_points) > 0:
                        current_point = curve_points[-1]

            elif command_name == "curveTo":
                if current_point is not None:
                    curve_points = self._curve_to_points(
                        current_point=current_point,
                        command_args=command_args,
                    )

                    for point in curve_points:
                        current_points.append(point)

                    if len(curve_points) > 0:
                        current_point = curve_points[-1]

            elif command_name == "closePath":
                if start_point is not None:
                    current_points.append(start_point)

                if len(current_points) > 0:
                    paths.append(
                        FontOutlinePath(
                            points=current_points,
                            closed=True,
                        )
                    )

                current_points = []
                current_point = None
                start_point = None

        if len(current_points) > 0:
            paths.append(
                FontOutlinePath(
                    points=current_points,
                    closed=False,
                )
            )

        return FontOutlineGlyph(
            text=text,
            paths=paths,
        )

    def _qcurve_to_points(
        self,
        current_point: FontPoint,
        command_args: Tuple[Any, ...],
    ) -> List[FontPoint]:
        """TrueTypeの2次ベジェ命令を点列へ変換する。"""
        q_points = list(command_args)

        if len(q_points) == 0:
            return []

        if q_points[-1] is None:
            q_points = q_points[:-1]

        if len(q_points) == 0:
            return []

        points: List[FontPoint] = []
        p0 = current_point

        if len(q_points) == 1:
            end_point = FontPoint(
                x=float(q_points[0][0]),
                y=float(q_points[0][1]),
            )
            return self._quadratic_bezier(
                p0=p0,
                p1=p0,
                p2=end_point,
            )

        for index in range(0, len(q_points) - 1):
            raw_control = q_points[index]
            raw_next = q_points[index + 1]

            control_point = FontPoint(
                x=float(raw_control[0]),
                y=float(raw_control[1]),
            )

            if index == len(q_points) - 2:
                end_point = FontPoint(
                    x=float(raw_next[0]),
                    y=float(raw_next[1]),
                )
            else:
                end_point = FontPoint(
                    x=0.5 * (float(raw_control[0]) + float(raw_next[0])),
                    y=0.5 * (float(raw_control[1]) + float(raw_next[1])),
                )

            segment_points = self._quadratic_bezier(
                p0=p0,
                p1=control_point,
                p2=end_point,
            )

            for point in segment_points:
                points.append(point)

            p0 = end_point

        return points

    def _curve_to_points(
        self,
        current_point: FontPoint,
        command_args: Tuple[Any, ...],
    ) -> List[FontPoint]:
        """3次ベジェ命令を点列へ変換する。"""
        p1 = FontPoint(
            x=float(command_args[0][0]),
            y=float(command_args[0][1]),
        )
        p2 = FontPoint(
            x=float(command_args[1][0]),
            y=float(command_args[1][1]),
        )
        p3 = FontPoint(
            x=float(command_args[2][0]),
            y=float(command_args[2][1]),
        )

        return self._cubic_bezier(
            p0=current_point,
            p1=p1,
            p2=p2,
            p3=p3,
        )

    def _quadratic_bezier(
        self,
        p0: FontPoint,
        p1: FontPoint,
        p2: FontPoint,
    ) -> List[FontPoint]:
        """2次ベジェ曲線を指定分割数で点列化する。"""
        points: List[FontPoint] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)
            one_minus_t = 1.0 - t

            x = one_minus_t * one_minus_t * p0.x
            x = x + 2.0 * one_minus_t * t * p1.x
            x = x + t * t * p2.x

            y = one_minus_t * one_minus_t * p0.y
            y = y + 2.0 * one_minus_t * t * p1.y
            y = y + t * t * p2.y

            points.append(FontPoint(x=x, y=y))

        return points

    def _cubic_bezier(
        self,
        p0: FontPoint,
        p1: FontPoint,
        p2: FontPoint,
        p3: FontPoint,
    ) -> List[FontPoint]:
        """3次ベジェ曲線を指定分割数で点列化する。"""
        points: List[FontPoint] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)
            one_minus_t = 1.0 - t

            x = one_minus_t * one_minus_t * one_minus_t * p0.x
            x = x + 3.0 * one_minus_t * one_minus_t * t * p1.x
            x = x + 3.0 * one_minus_t * t * t * p2.x
            x = x + t * t * t * p3.x

            y = one_minus_t * one_minus_t * one_minus_t * p0.y
            y = y + 3.0 * one_minus_t * one_minus_t * t * p1.y
            y = y + 3.0 * one_minus_t * t * t * p2.y
            y = y + t * t * t * p3.y

            points.append(FontPoint(x=x, y=y))

        return points

    def _scale_outline_glyph(
        self,
        outline_glyph: FontOutlineGlyph,
    ) -> FontOutlineGlyph:
        """フォント座標を指定高さの座標へ変換する。"""
        scaled_paths: List[FontOutlinePath] = []

        for path in outline_glyph:
            scaled_points: List[FontPoint] = []

            for point in path:
                scaled_points.append(point.scaled(scale=self._scale))

            scaled_paths.append(
                FontOutlinePath(
                    points=scaled_points,
                    closed=path.closed,
                )
            )

        return FontOutlineGlyph(
            text=outline_glyph.text,
            paths=scaled_paths,
        )


def main() -> None:
    """フォント輪郭抽出を単体確認する。"""
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

    print(outline)
    print(len(outline))


if __name__ == "__main__":
    main()
