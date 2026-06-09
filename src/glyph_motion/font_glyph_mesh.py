from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from font_geometry import GlyphMesh
from font_geometry import MeshPath
from font_geometry import MeshPoint


class FontGlyphMesh:
    """フォントファイルから文字グリフのメッシュ座標を作るクラスである。"""

    def __init__(
        self,
        font_file: Path,
        height: float = 40.0,
        curve_division: int = 8,
    ) -> None:
        self._font_file = font_file
        self._height = height
        self._curve_division = curve_division

        self._font = TTFont(str(self._font_file))
        self._cmap = self._font.getBestCmap()
        self._glyph_set = self._font.getGlyphSet()

        units_per_em = float(self._font["head"].unitsPerEm)
        self._scale = self._height / units_per_em

    def get_character_mesh(
        self,
        character: str,
    ) -> GlyphMesh:
        """1文字のグリフメッシュを取得する。"""
        glyph_name = self._get_glyph_name(
            character=character,
        )

        glyph = self._glyph_set[glyph_name]

        pen = RecordingPen()
        glyph.draw(pen)

        glyph_mesh = self._recording_to_glyph_mesh(
            recording=pen.value,
        )

        return glyph_mesh.scaled(
            scale=self._scale,
        )

    def get_text_mesh(
        self,
        text: str,
        spacing: float = 5.0,
    ) -> GlyphMesh:
        """文字列のグリフメッシュを取得する。"""
        result_mesh = GlyphMesh(
            paths=[],
        )

        x_offset = 0.0

        for character in text:
            character_mesh = self.get_character_mesh(
                character=character,
            )

            shifted_mesh = character_mesh.shifted(
                x_offset=x_offset,
                y_offset=0.0,
            )

            result_mesh.extend(
                glyph_mesh=shifted_mesh,
            )

            glyph_name = self._get_glyph_name(
                character=character,
            )

            advance_width = self._font["hmtx"].metrics[glyph_name][0]
            x_offset = x_offset + float(advance_width) * self._scale
            x_offset = x_offset + spacing

        return result_mesh

    def _get_glyph_name(
        self,
        character: str,
    ) -> str:
        """文字に対応するグリフ名を取得する。"""
        code_point = ord(character)

        if code_point not in self._cmap:
            raise ValueError(
                "フォントに含まれていない文字である: {}".format(character)
            )

        glyph_name = self._cmap[code_point]

        return glyph_name

    def _recording_to_glyph_mesh(
        self,
        recording: List[Tuple[str, Tuple[Any, ...]]],
    ) -> GlyphMesh:
        """RecordingPenの命令列をGlyphMeshへ変換する。"""
        glyph_mesh = GlyphMesh(
            paths=[],
        )

        current_points: List[MeshPoint] = []
        current_point: Optional[MeshPoint] = None
        start_point: Optional[MeshPoint] = None

        for command_name, command_args in recording:
            if command_name == "moveTo":
                if len(current_points) > 0:
                    glyph_mesh.append(
                        path=MeshPath(
                            points=current_points,
                            closed=False,
                        )
                    )

                point = command_args[0]
                current_point = MeshPoint(
                    x=float(point[0]),
                    y=float(point[1]),
                )
                start_point = current_point
                current_points = [
                    current_point,
                ]

            elif command_name == "lineTo":
                point = command_args[0]
                current_point = MeshPoint(
                    x=float(point[0]),
                    y=float(point[1]),
                )
                current_points.append(current_point)

            elif command_name == "qCurveTo":
                if current_point is not None:
                    curve_points = self._qcurve_to_points(
                        current_point=current_point,
                        command_args=command_args,
                    )

                    for curve_point in curve_points:
                        current_points.append(curve_point)

                    if len(curve_points) > 0:
                        current_point = curve_points[-1]

            elif command_name == "curveTo":
                if current_point is not None:
                    curve_points = self._curve_to_points(
                        current_point=current_point,
                        command_args=command_args,
                    )

                    for curve_point in curve_points:
                        current_points.append(curve_point)

                    if len(curve_points) > 0:
                        current_point = curve_points[-1]

            elif command_name == "closePath":
                if start_point is not None:
                    current_points.append(start_point)

                if len(current_points) > 0:
                    glyph_mesh.append(
                        path=MeshPath(
                            points=current_points,
                            closed=True,
                        )
                    )

                current_points = []
                current_point = None
                start_point = None

        if len(current_points) > 0:
            glyph_mesh.append(
                path=MeshPath(
                    points=current_points,
                    closed=False,
                )
            )

        return glyph_mesh

    def _qcurve_to_points(
        self,
        current_point: MeshPoint,
        command_args: Tuple[Any, ...],
    ) -> List[MeshPoint]:
        """2次ベジェ曲線命令を点列へ変換する。"""
        q_points = list(command_args)

        if len(q_points) < 2:
            return []

        points: List[MeshPoint] = []
        p0 = current_point

        for index in range(0, len(q_points) - 1):
            raw_control = q_points[index]
            raw_end = q_points[index + 1]

            control_point = MeshPoint(
                x=float(raw_control[0]),
                y=float(raw_control[1]),
            )

            end_point = MeshPoint(
                x=float(raw_end[0]),
                y=float(raw_end[1]),
            )

            if index < len(q_points) - 2:
                end_point = MeshPoint(
                    x=0.5 * (float(raw_control[0]) + float(raw_end[0])),
                    y=0.5 * (float(raw_control[1]) + float(raw_end[1])),
                )

            segment_points = self._quadratic_bezier(
                p0=p0,
                p1=control_point,
                p2=end_point,
            )

            for segment_point in segment_points:
                points.append(segment_point)

            p0 = end_point

        return points

    def _curve_to_points(
        self,
        current_point: MeshPoint,
        command_args: Tuple[Any, ...],
    ) -> List[MeshPoint]:
        """3次ベジェ曲線命令を点列へ変換する。"""
        point_1 = MeshPoint(
            x=float(command_args[0][0]),
            y=float(command_args[0][1]),
        )
        point_2 = MeshPoint(
            x=float(command_args[1][0]),
            y=float(command_args[1][1]),
        )
        point_3 = MeshPoint(
            x=float(command_args[2][0]),
            y=float(command_args[2][1]),
        )

        return self._cubic_bezier(
            p0=current_point,
            p1=point_1,
            p2=point_2,
            p3=point_3,
        )

    def _quadratic_bezier(
        self,
        p0: MeshPoint,
        p1: MeshPoint,
        p2: MeshPoint,
    ) -> List[MeshPoint]:
        """2次ベジェ曲線を点列へ分割する。"""
        points: List[MeshPoint] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)

            x = (1.0 - t) * (1.0 - t) * p0.x
            x = x + 2.0 * (1.0 - t) * t * p1.x
            x = x + t * t * p2.x

            y = (1.0 - t) * (1.0 - t) * p0.y
            y = y + 2.0 * (1.0 - t) * t * p1.y
            y = y + t * t * p2.y

            points.append(
                MeshPoint(
                    x=x,
                    y=y,
                )
            )

        return points

    def _cubic_bezier(
        self,
        p0: MeshPoint,
        p1: MeshPoint,
        p2: MeshPoint,
        p3: MeshPoint,
    ) -> List[MeshPoint]:
        """3次ベジェ曲線を点列へ分割する。"""
        points: List[MeshPoint] = []

        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)

            x = (1.0 - t) ** 3 * p0.x
            x = x + 3.0 * (1.0 - t) ** 2 * t * p1.x
            x = x + 3.0 * (1.0 - t) * t * t * p2.x
            x = x + t ** 3 * p3.x

            y = (1.0 - t) ** 3 * p0.y
            y = y + 3.0 * (1.0 - t) ** 2 * t * p1.y
            y = y + 3.0 * (1.0 - t) * t * t * p2.y
            y = y + t ** 3 * p3.y

            points.append(
                MeshPoint(
                    x=x,
                    y=y,
                )
            )

        return points


def main() -> None:
    font_file = Path("NotoSansCJKjp-Regular.otf")

    if font_file.exists() is False:
        print("NotoSansCJKjp-Regular.otf が見つからない。")
        return

    font_glyph_mesh = FontGlyphMesh(
        font_file=font_file,
        height=40.0,
        curve_division=8,
    )

    glyph_mesh = font_glyph_mesh.get_text_mesh(
        text="島",
        spacing=5.0,
    )

    print(glyph_mesh)
    print("path_count =", len(glyph_mesh))


if __name__ == "__main__":
    main()