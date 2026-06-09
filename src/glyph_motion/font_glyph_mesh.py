from pathlib import Path
from typing import Any, List, Optional, Tuple

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from font_geometry import GlyphMesh, MeshPath, MeshPoint


class FontGlyphMesh:
    """フォントファイルから文字グリフのメッシュ座標を生成するクラスである。

    TrueType/OpenTypeフォントのアウトライン情報を解析し、直線およびベジェ曲線を点列に展開する。
    """

    def __init__(
        self,
        font_file: Path,
        height: float = 40.0,
        curve_division: int = 8,
    ) -> None:
        """指定されたフォントファイルとパラメータで初期化を行う。

        Args:
            font_file (Path): 読み込むフォントファイルのパス。
            height (float): 出力する文字の基準高さ（デザインサイズ）。
            curve_division (int): ベジェ曲線を直線分割する際の分割数。
        """
        self._font_file = font_file
        self._height = height
        self._curve_division = curve_division

        self._font = TTFont(str(self._font_file))
        self._cmap = self._font.getBestCmap()
        self._glyph_set = self._font.getGlyphSet()

        units_per_em = float(self._font["head"].unitsPerEm)
        self._scale = self._height / units_per_em

    def get_character_mesh(self, character: str) -> GlyphMesh:
        """指定された1文字のグリフメッシュを取得する。

        フォント固有のスケール（unitsPerEmからheightへの比率）が適用された座標が出力される。

        Args:
            character (str): メッシュ化対象の単一文字。

        Returns:
            GlyphMesh: スケール調整済みの幾何メッシュデータ。
        """
        glyph_name = self._get_glyph_name(character=character)
        glyph = self._glyph_set[glyph_name]

        pen = RecordingPen()
        glyph.draw(pen)

        glyph_mesh = self._recording_to_glyph_mesh(recording=pen.value)
        return glyph_mesh.scaled(scale=self._scale)

    def get_text_mesh(self, text: str, spacing: float = 5.0) -> GlyphMesh:
        """文字列全体のグリフメッシュを、文字送りを考慮して生成・結合する。

        Args:
            text (str): メッシュ化対象の文字列。
            spacing (float): 文字間の隙間（余白）の大きさ。

        Returns:
            GlyphMesh: 各文字が適切な位置に整列・結合されたメッシュデータ。
        """
        result_mesh = GlyphMesh(paths=[])
        x_offset = 0.0

        for character in text:
            character_mesh = self.get_character_mesh(character=character)
            shifted_mesh = character_mesh.shifted(x_offset=x_offset, y_offset=0.0)
            result_mesh.extend(glyph_mesh=shifted_mesh)

            glyph_name = self._get_glyph_name(character=character)
            advance_width = self._font["hmtx"].metrics[glyph_name][0]
            x_offset = x_offset + float(advance_width) * self._scale
            x_offset = x_offset + spacing

        return result_mesh

    def _get_glyph_name(self, character: str) -> str:
        """文字に対応するフォント内部のグリフ名を取得する。

        Args:
            character (str): 対象の文字。

        Returns:
            str: フォント内のグリフ識別名。

        Raises:
            ValueError: フォントのマッピングテーブル（cmap）に対象文字が存在しない場合。
        """
        code_point = ord(character)
        if code_point not in self._cmap:
            raise ValueError(
                "フォントに含まれていない文字である: {}".format(character)
            )
        return self._cmap[code_point]

    def _recording_to_glyph_mesh(
        self, recording: List[Tuple[str, Tuple[Any, ...]]]
    ) -> GlyphMesh:
        """RecordingPenの描画命令列を解析し、GlyphMesh構造体へ変換する。

        Args:
            recording (List[Tuple[str, Tuple[Any, ...]]]): RecordingPenから取得したコマンドリスト。

        Returns:
            GlyphMesh: 未スケールのグリフメッシュデータ。
        """
        glyph_mesh = GlyphMesh(paths=[])
        current_points: List[MeshPoint] = []
        current_point: Optional[MeshPoint] = None
        start_point: Optional[MeshPoint] = None

        for command_name, command_args in recording:
            if command_name == "moveTo":
                if len(current_points) > 0:
                    glyph_mesh.append(
                        path=MeshPath(points=current_points, closed=False)
                    )
                point = command_args[0]
                current_point = MeshPoint(x=float(point[0]), y=float(point[1]))
                start_point = current_point
                current_points = [current_point]

            elif command_name == "lineTo":
                point = command_args[0]
                current_point = MeshPoint(x=float(point[0]), y=float(point[1]))
                current_points.append(current_point)

            elif command_name == "qCurveTo":
                if current_point is not None:
                    curve_points = self._qcurve_to_points(
                        current_point=current_point, command_args=command_args
                    )
                    for curve_point in curve_points:
                        current_points.append(curve_point)
                    if len(curve_points) > 0:
                        current_point = curve_points[-1]

            elif command_name == "curveTo":
                if current_point is not None:
                    curve_points = self._curve_to_points(
                        current_point=current_point, command_args=command_args
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
                        path=MeshPath(points=current_points, closed=True)
                    )
                current_points = []
                current_point = None
                start_point = None

        if len(current_points) > 0:
            glyph_mesh.append(
                path=MeshPath(points=current_points, closed=False)
            )

        return glyph_mesh

    def _qcurve_to_points(
        self, current_point: MeshPoint, command_args: Tuple[Any, ...]
    ) -> List[MeshPoint]:
        """2次ベジェ曲線命令（複数の制御点を含む場合を考慮）を点列へ変換する。

        Args:
            current_point (MeshPoint): 描画の現在の開始点。
            command_args (Tuple[Any, ...]): 制御点および終点の座標リスト。

        Returns:
            List[MeshPoint]: 補間された点列。
        """
        q_points = list(command_args)
        if len(q_points) < 1:
            return []

        # 最後の要素が終点、それ以外が制御点（TrueType特有の連続制御点への対応）
        points: List[MeshPoint] = []
        p0 = current_point

        for index in range(0, len(q_points)):
            raw_control = q_points[index]

            # 最後の1点である場合はそれが最終終点となる
            if index == len(q_points) - 1:
                end_point = MeshPoint(
                    x=float(raw_control[0]), y=float(raw_control[1])
                )
                # 制御点が省略された直線として補間
                segment_points = self._quadratic_bezier(
                    p0=p0, p1=p0, p2=end_point
                )
                points.extend(segment_points)
                break

            control_point = MeshPoint(
                x=float(raw_control[0]), y=float(raw_control[1])
            )
            raw_next = q_points[index + 1]

            # 次が最後の点ならそれが終点、連続制御点なら中間点を終点とする
            if index == len(q_points) - 2:
                end_point = MeshPoint(
                    x=float(raw_next[0]), y=float(raw_next[1])
                )
                segment_points = self._quadratic_bezier(
                    p0=p0, p1=control_point, p2=end_point
                )
                points.extend(segment_points)
                break
            else:
                end_point = MeshPoint(
                    x=0.5 * (float(raw_control[0]) + float(raw_next[0])),
                    y=0.5 * (float(raw_control[1]) + float(raw_next[1])),
                )
                segment_points = self._quadratic_bezier(
                    p0=p0, p1=control_point, p2=end_point
                )
                points.extend(segment_points)
                p0 = end_point

        return points

    def _curve_to_points(
        self, current_point: MeshPoint, command_args: Tuple[Any, ...]
    ) -> List[MeshPoint]:
        """3次ベジェ曲線命令を点列へ変換する。

        Args:
            current_point (MeshPoint): 描画の現在の開始点。
            command_args (Tuple[Any, ...]): 3つの座標対（制御点1、制御点2、終点）。

        Returns:
            List[MeshPoint]: 補間された点列。
        """
        point_1 = MeshPoint(
            x=float(command_args[0][0]), y=float(command_args[0][1])
        )
        point_2 = MeshPoint(
            x=float(command_args[1][0]), y=float(command_args[1][1])
        )
        point_3 = MeshPoint(
            x=float(command_args[2][0]), y=float(command_args[2][1])
        )

        return self._cubic_bezier(
            p0=current_point, p1=point_1, p2=point_2, p3=point_3
        )

    def _quadratic_bezier(
        self, p0: MeshPoint, p1: MeshPoint, p2: MeshPoint
    ) -> List[MeshPoint]:
        """2次ベジェ曲線を数式に基づき指定分割数でサンプリングする。"""
        points: List[MeshPoint] = []
        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)
            x = (1.0 - t) * (1.0 - t) * p0.x + 2.0 * (1.0 - t) * t * p1.x + t * t * p2.x
            y = (1.0 - t) * (1.0 - t) * p0.y + 2.0 * (1.0 - t) * t * p1.y + t * t * p2.y
            points.append(MeshPoint(x=x, y=y))
        return points

    def _cubic_bezier(
        self, p0: MeshPoint, p1: MeshPoint, p2: MeshPoint, p3: MeshPoint
    ) -> List[MeshPoint]:
        """3次ベジェ曲線を数式に基づき指定分割数でサンプリングする。"""
        points: List[MeshPoint] = []
        for index in range(1, self._curve_division + 1):
            t = float(index) / float(self._curve_division)
            x = (1.0 - t) ** 3 * p0.x + 3.0 * (1.0 - t) ** 2 * t * p1.x + 3.0 * (1.0 - t) * t * t * p2.x + t ** 3 * p3.x
            y = (1.0 - t) ** 3 * p0.y + 3.0 * (1.0 - t) ** 2 * t * p1.y + 3.0 * (1.0 - t) * t * t * p2.y + t ** 3 * p3.y
            points.append(MeshPoint(x=x, y=y))
        return points


def main() -> None:
    """フォントファイルが存在する場合に、単一文字のメッシュ化およびパス数を検証する。"""
    font_file = Path("NotoSansCJKjp-Regular.otf")

    if font_file.exists() is False:
        print("NotoSansCJKjp-Regular.otf が見つからないため検証をスキップする。")
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