"""
K.NAKADA, kengo.nakada@gmail.com

文字列をロボット筆記用の相対移動命令へ変換する簡易 I/F を定義する。

このモジュールの主目的は、次の入口を提供することである。

    writer.write("島")
    writer.write("島根", layout="horizontal")
    writer.write("島根", layout="vertical")

このクラスは、KanjiVG 読み込み、複数文字の配置、ロボット向け相対移動命令生成を
簡単に呼び出すための薄い I/F である。

ロボット固有 API は呼ばない。
write() は FontRobotMotionCommand のリストを返す。
"""

from pathlib import Path
from typing import List

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokeGlyph
from glyph_motion.lib.font_geometry import FontStrokePath
from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader

from glyph_motion.font_robot_motion_builder import FontRobotMotionBuilder
from glyph_motion.font_robot_motion_builder import FontRobotMotionCommand


class FontRobotWriter:
    """write() で文字列をロボット筆記用相対移動命令へ変換する。"""

    def __init__(
        self,
        kanjivg_directory: Path,
        height: float,
        character_spacing: float,
        pen_lift_height: float,
        curve_division: int = 20,
        drawing_speed: float = 10.0,
        travel_speed: float = 30.0,
    ) -> None:
        """KanjiVG 読み込み条件、文字配置条件、ロボット移動条件を設定する。"""
        if height <= 0.0:
            raise ValueError("height は正の値である必要がある。")

        if character_spacing < 0.0:
            raise ValueError("character_spacing は0以上である必要がある。")

        self._height = height
        self._character_spacing = character_spacing

        self._loader = FontKanjiVGStrokeLoader(
            kanjivg_directory=kanjivg_directory,
            height=height,
            spacing=character_spacing,
            curve_division=curve_division,
        )

        self._motion_builder = FontRobotMotionBuilder(
            pen_lift_height=pen_lift_height,
            drawing_speed=drawing_speed,
            travel_speed=travel_speed,
        )

    def write(
        self,
        text: str,
        layout: str = "horizontal",
    ) -> List[FontRobotMotionCommand]:
        """文字列をロボット筆記用相対移動命令へ変換する。

        Args:
            text: 書く文字列である。
            layout: "horizontal" または "vertical" を指定する。

        Returns:
            FontRobotMotionCommand のリストである。
        """
        stroke_glyph = self.build_stroke_glyph(
            text=text,
            layout=layout,
        )

        return self._motion_builder.build(
            stroke_glyph=stroke_glyph,
        )

    def build_stroke_glyph(
        self,
        text: str,
        layout: str = "horizontal",
    ) -> FontStrokeGlyph:
        """文字列から配置済み FontStrokeGlyph を作る。"""
        if layout == "horizontal":
            return self._build_horizontal_stroke_glyph(
                text=text,
            )

        if layout == "vertical":
            return self._build_vertical_stroke_glyph(
                text=text,
            )

        raise ValueError("layout は horizontal または vertical である必要がある。")

    def _build_horizontal_stroke_glyph(
        self,
        text: str,
    ) -> FontStrokeGlyph:
        """横書き配置で FontStrokeGlyph を作る。"""
        stroke_paths: List[FontStrokePath] = []
        x_offset = 0.0

        for character in text:
            if character == " ":
                x_offset = x_offset + self._height + self._character_spacing
                continue

            character_glyph, advance_width = self._loader.load_character(
                character=character,
            )

            for stroke_path in character_glyph:
                stroke_paths.append(
                    self._shift_stroke_path(
                        stroke_path=stroke_path,
                        x_offset=x_offset,
                        y_offset=0.0,
                    )
                )

            x_offset = x_offset + advance_width + self._character_spacing

        return FontStrokeGlyph(
            text=text,
            paths=stroke_paths,
        )

    def _build_vertical_stroke_glyph(
        self,
        text: str,
    ) -> FontStrokeGlyph:
        """縦書き配置で FontStrokeGlyph を作る。"""
        stroke_paths: List[FontStrokePath] = []
        y_offset = 0.0

        for character in text:
            if character == " ":
                y_offset = y_offset - self._height - self._character_spacing
                continue

            character_glyph, advance_width = self._loader.load_character(
                character=character,
            )

            for stroke_path in character_glyph:
                stroke_paths.append(
                    self._shift_stroke_path(
                        stroke_path=stroke_path,
                        x_offset=0.0,
                        y_offset=y_offset,
                    )
                )

            y_offset = y_offset - advance_width - self._character_spacing

        return FontStrokeGlyph(
            text=text,
            paths=stroke_paths,
        )

    def _shift_stroke_path(
        self,
        stroke_path: FontStrokePath,
        x_offset: float,
        y_offset: float,
    ) -> FontStrokePath:
        """FontStrokePath を指定量だけ平行移動する。"""
        shifted_points: List[FontPoint] = []

        for point in stroke_path:
            shifted_points.append(
                FontPoint(
                    x=point.x + x_offset,
                    y=point.y + y_offset,
                )
            )

        return FontStrokePath(
            points=shifted_points,
        )


def main() -> None:
    """FontRobotWriter の単体動作を確認する。"""
    kanjivg_directory = Path(__file__).resolve().parent / "data" / "kanjiVG"

    writer = FontRobotWriter(
        kanjivg_directory=kanjivg_directory,
        height=40.0,
        character_spacing=5.0,
        pen_lift_height=5.0,
        curve_division=20,
        drawing_speed=10.0,
        travel_speed=30.0,
    )

    commands = writer.write(
        text="島根",
        layout="horizontal",
    )

    for command in commands:
        print(command)


if __name__ == "__main__":
    main()
