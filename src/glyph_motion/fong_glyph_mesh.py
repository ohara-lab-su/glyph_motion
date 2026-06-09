from pathlib import Path
from typing import Optional

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont


class FontGlyphMesh:
    """フォントから文字アウトライン座標を取り出すクラス"""

    def __init__(
        self,
        font_file: Path,
        height_mm: float = 40.0,
        curve_division: int = 8,
    ) -> None:
        self._font_file = font_file
        self._height_mm = height_mm
        self._curve_division = curve_division

        self._font = TTFont(str(self._font_file))
        self._cmap = self._font.getBestCmap()
        self._glyph_set = self._font.getGlyphSet()
        self._units_per_em = float(self._font["head"].unitsPerEm)
        self._scale = self._height_mm / self._units_per_em

    def get_character_mesh(
        self,
        character: str,
    ) -> list[list[tuple[float, float]]]:
        """1文字の輪郭をXY座標列として取得する。"""
        glyph_name = self._get_glyph_name(character)
        glyph = self._glyph_set[glyph_name]

        pen = RecordingPen()
        glyph.draw(pen)

        contours = self._recording_to_contours(pen.value)

        scaled_contours = self._scale_contours(contours)

        return scaled_contours

    def get_text_mesh(
        self,
        text: str,
        spacing_mm: float = 5.0,
    ) -> list[list[tuple[float, float]]]:
        """文字列の輪郭をXY座標列として取得する。"""
        text_contours: list[list[tuple[float, float]]] = []
        x_offset = 0.0

        for character in text:
            character_contours = self.get_character_mesh(character)

            shifted_contours = self._shift_contours(
                contours=character_contours,
                x_offset=x_offset,
                y_offset=0.0,
            )

            text_contours.extend(shifted_contours)

            glyph_name = self._get_glyph_name(character)
            advance_width = self._font["hmtx"].metrics[glyph_name][0]
            x_advance = float(advance_width) * self._scale
            x_offset = x_offset + x_advance
            x_offset = x_offset + spacing_mm

        return text_contours

    def _get_glyph_name(
        self,
        character: str,
    ) -> str:
        """文字に対応するグリフ名を取得する。"""
        code_point = ord(character)

        if code_point not in self._cmap:
            raise ValueError(f"フォントに文字が含まれていない: {character}")

        glyph_name = self._cmap[code_point]

        return glyph_name

    def _recording_to_contours(
        self,
        recording: list[tuple[str, tuple]],
    ) -> list[list[tuple[float, float]]]:
        """RecordingPenの記録を輪郭座標列へ変換する。"""
        contours: list[list[tuple[float, float]]] = []

        current_contour: list[tuple[float, float]] = []
        current_point: Optional[tuple[float, float]] = None
        start_point: Optional[tuple[float, float]] = None

        for command_name, command_args in recording:
            if command_name == "moveTo":
                if len(current_contour) > 0:
                    contours.append(current_contour)

                point = command_args[0]
                current_point = (float(point[0]), float(point[1]))
                start_point = current_point
                current_contour = [current_point]

            elif command_name == "lineTo":
                point = command_args[0]
                current_point = (float(point[0]), float(point[1]))
                current_contour.append(current_point)

            elif command_name == "qCurveTo":
                if current_point is None:
                    continue

                curve_points = self._qcurve_to_points(
                    current_point=current_point,
                    command_args=command_args,
                )

                current_contour.extend(curve_points)

                if len(curve_points) > 0:
                    current_point = curve_points[-1]

            elif command_name == "curveTo":
                if current_point is None:
                    continue

                curve_points = self._curve_to_points(
                    current_point=current_point,
                    command_args=command_args,
                )

                current_contour.extend(curve_points)

                if len(curve_points) > 0:
                    current_point = curve_points[-1]

            elif command_name == "closePath":
                if start_point is not None:
                    current_contour.append(start_point)

                if len(current_contour) > 0:
                    contours.append(current_contour)

                current_contour = []
                current_point = None
                start_point = None

        if len(current_contour) > 0:
            contours.append(current_contour)

        return contours

    def _qcurve_to_points(
        self,
        current_point: tuple[float, float],
        command_args: tuple,
    ) -> list[tuple[float, float]]:
        """2次ベジェ曲線命令を点列へ変換する。"""
        q_points = list(command_args)

        if len(q_points) < 2:
            return []

        control = q_points[0]
        end = q_points[-1]

        control_point = (float(control[0]), float(control[1]))
        end_point = (float(end[0]), float(end[1]))

        points = self._quadratic_bezier(
            p0=current_point,
            p1=control_point,
            p2=end_point,
        )

        return points

    def _curve_to_points(
        self,
        current_point: tuple[float, float],
        command_args: tuple,
    ) -> list[tuple[float, float]]:
        """3次ベジェ曲線命令を点列へ変換する。"""
        p1 = command_args[0]
        p2 = command_args[1]
        p3 = command_args[2]

        point1 = (float(p1[0]), float(p1[1]))
        point2 = (float(p2[0]), float(p2[1]))
        point3 = (float(p3[0]), float(p3[1]))

        points = self._cubic_bezier(
            p0=current_point,
            p1=point1,
            p2=point2,
            p3=point3,
        )

        return points

    def _quadratic_bezier(
        self,
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
    ) -> list[tuple[float, float]]:
        """2次ベジェ曲線を折線点列に分割する。"""
        points: list[tuple[float, float]] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)

            x = (1.0 - t) * (1.0 - t) * p0[0]
            x = x + 2.0 * (1.0 - t) * t * p1[0]
            x = x + t * t * p2[0]

            y = (1.0 - t) * (1.0 - t) * p0[1]
            y = y + 2.0 * (1.0 - t) * t * p1[1]
            y = y + t * t * p2[1]

            points.append((x, y))

        return points

    def _cubic_bezier(
        self,
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
    ) -> list[tuple[float, float]]:
        """3次ベジェ曲線を折線点列に分割する。"""
        points: list[tuple[float, float]] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)

            x = (1.0 - t) ** 3 * p0[0]
            x = x + 3.0 * (1.0 - t) ** 2 * t * p1[0]
            x = x + 3.0 * (1.0 - t) * t * t * p2[0]
            x = x + t ** 3 * p3[0]

            y = (1.0 - t) ** 3 * p0[1]
            y = y + 3.0 * (1.0 - t) ** 2 * t * p1[1]
            y = y + 3.0 * (1.0 - t) * t * t * p2[1]
            y = y + t ** 3 * p3[1]

            points.append((x, y))

        return points

    def _scale_contours(
        self,
        contours: list[list[tuple[float, float]]],
    ) -> list[list[tuple[float, float]]]:
        """フォント座標をmm座標へ変換する。"""
        scaled_contours: list[list[tuple[float, float]]] = []

        for contour in contours:
            scaled_contour: list[tuple[float, float]] = []

            for x_font, y_font in contour:
                x_mm = x_font * self._scale
                y_mm = y_font * self._scale
                scaled_contour.append((x_mm, y_mm))

            scaled_contours.append(scaled_contour)

        return scaled_contours

    def _shift_contours(
        self,
        contours: list[list[tuple[float, float]]],
        x_offset: float,
        y_offset: float,
    ) -> list[list[tuple[float, float]]]:
        """輪郭座標列を平行移動する。"""
        shifted_contours: list[list[tuple[float, float]]] = []

        for contour in contours:
            shifted_contour: list[tuple[float, float]] = []

            for x_mm, y_mm in contour:
                shifted_x = x_mm + x_offset
                shifted_y = y_mm + y_offset
                shifted_contour.append((shifted_x, shifted_y))

            shifted_contours.append(shifted_contour)

        return shifted_contours


def main() -> None:
    font_mesh = FontGlyphMesh(
        font_file=Path("NotoSansCJKjp-Regular.otf"),
        height_mm=40.0,
        curve_division=8,
    )

    contours = font_mesh.get_text_mesh(
        text="島根",
        spacing_mm=5.0,
    )

    for contour_index, contour in enumerate(contours):
        print(f"contour {contour_index}")

        for x_mm, y_mm in contour:
            print(f"{x_mm:.3f}, {y_mm:.3f}")


if __name__ == "__main__":
    main()