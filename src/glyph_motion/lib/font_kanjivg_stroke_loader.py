#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

KanjiVG の SVG ファイルから筆順付き stroke データを読み込む。
 [oai_citation:1‡KanjiVG](https://kanjivg.tagaini.net/svg-format.html?utm_source=chatgpt.com)つ SVG path を読み取り、FontStrokeGlyph に変換する。

KanjiVG の StrokePaths グループには、漢字の各筆画が SVG path として
筆順順に格納されている。この順序をそのままロボット筆記順として使う。

このモジュールは、漢字用の本命ルートである。

KanjiVG SVG
->
FontStrokeGlyph
->
FontMotionBuilder

という流れで使う。
"""

import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import List, Optional, Tuple

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokeGlyph
from glyph_motion.lib.font_geometry import FontStrokePath


SvgCommand = Tuple[str, List[float]]


class FontKanjiVGStrokeLoader:
    """KanjiVG SVG から筆順付き FontStrokeGlyph を生成するクラスである。"""

    def __init__(
        self,
        kanjivg_directory: Path,
        height: float,
        spacing: float,
        curve_division: int = 16,
    ) -> None:
        """KanjiVG ディレクトリ、出力文字高さ、文字間隔、曲線分割数を設定する。"""
        if height <= 0.0:
            raise ValueError("height は正の値である必要がある。")

        if spacing < 0.0:
            raise ValueError("spacing は0以上である必要がある。")

        if curve_division < 1:
            raise ValueError("curve_division は1以上である必要がある。")

        self._kanjivg_directory = kanjivg_directory
        self._height = height
        self._spacing = spacing
        self._curve_division = curve_division
        self._path_sampler = SvgPathSampler(
            curve_division=curve_division,
        )

    def load_text(
        self,
        text: str,
    ) -> FontStrokeGlyph:
        """文字列を KanjiVG 由来の筆順付き stroke データとして読み込む。"""
        stroke_paths: List[FontStrokePath] = []
        x_offset = 0.0

        for character in text:
            if character == " ":
                x_offset = x_offset + self._height + self._spacing
                continue

            character_glyph, advance_width = self.load_character(
                character=character,
            )

            for stroke_path in character_glyph:
                shifted_points: List[FontPoint] = []

                for point in stroke_path:
                    shifted_points.append(
                        FontPoint(
                            x=point.x + x_offset,
                            y=point.y,
                        )
                    )

                stroke_paths.append(
                    FontStrokePath(
                        points=shifted_points,
                    )
                )

            x_offset = x_offset + advance_width + self._spacing

        return FontStrokeGlyph(
            text=text,
            paths=stroke_paths,
        )

    def load_character(
        self,
        character: str,
    ) -> Tuple[FontStrokeGlyph, float]:
        """一文字の KanjiVG SVG を読み込み、筆順付き stroke データを返す。"""
        if len(character) != 1:
            raise ValueError("character は1文字である必要がある。")

        svg_file = self._find_svg_file(
            character=character,
        )

        tree = ElementTree.parse(str(svg_file))
        root = tree.getroot()

        view_box = self._read_view_box(
            root=root,
        )

        raw_paths = self._collect_stroke_paths(
            root=root,
        )

        if len(raw_paths) == 0:
            raise ValueError("KanjiVG SVG 内に stroke path が存在しない。")

        scale = self._height / view_box[3]
        advance_width = view_box[2] * scale

        stroke_paths: List[FontStrokePath] = []

        for raw_path in raw_paths:
            svg_points = self._path_sampler.sample_path(
                path_data=raw_path,
            )

            points: List[FontPoint] = []

            for point in svg_points:
                points.append(
                    self._convert_svg_point(
                        point=point,
                        view_box=view_box,
                        scale=scale,
                    )
                )

            if len(points) > 0:
                stroke_paths.append(
                    FontStrokePath(
                        points=points,
                    )
                )

        return (
            FontStrokeGlyph(
                text=character,
                paths=stroke_paths,
            ),
            advance_width,
        )

    def _find_svg_file(
        self,
        character: str,
    ) -> Path:
        """文字に対応する KanjiVG SVG ファイルを探す。"""
        code_point = ord(character)
        file_name = "{:05x}.svg".format(code_point)
        svg_file = self._kanjivg_directory / file_name

        if svg_file.exists() is False:
            raise FileNotFoundError("KanjiVG SVG が見つからない: {}".format(svg_file))

        return svg_file

    def _read_view_box(
        self,
        root,
    ) -> Tuple[float, float, float, float]:
        """SVG の viewBox を読み取る。"""
        view_box_text = root.attrib.get("viewBox")

        if view_box_text is None:
            return (
                0.0,
                0.0,
                109.0,
                109.0,
            )

        values = view_box_text.replace(",", " ").split()

        if len(values) != 4:
            raise ValueError("SVG viewBox の形式が不正である。")

        return (
            float(values[0]),
            float(values[1]),
            float(values[2]),
            float(values[3]),
        )

    def _collect_stroke_paths(
        self,
        root,
    ) -> List[str]:
        """StrokePaths グループ内の path d 属性を筆順順に集める。"""
        stroke_paths_group = self._find_stroke_paths_group(
            root=root,
        )

        if stroke_paths_group is None:
            raise ValueError("KanjiVG SVG に StrokePaths グループが存在しない。")

        raw_paths: List[str] = []

        for element in stroke_paths_group.iter():
            tag_name = self._strip_namespace(
                tag=element.tag,
            )

            if tag_name != "path":
                continue

            path_data = element.attrib.get("d")

            if path_data is None:
                continue

            raw_paths.append(path_data)

        return raw_paths

    def _find_stroke_paths_group(
        self,
        root,
    ):
        """id が kvg:StrokePaths で始まる SVG group を探す。"""
        for element in root.iter():
            tag_name = self._strip_namespace(
                tag=element.tag,
            )

            if tag_name != "g":
                continue

            element_id = element.attrib.get("id", "")

            if element_id.startswith("kvg:StrokePaths"):
                return element

        return None

    def _strip_namespace(
        self,
        tag: str,
    ) -> str:
        """XML 名前空間を除いたタグ名を返す。"""
        if "}" in tag:
            return tag.split("}", 1)[1]

        return tag

    def _convert_svg_point(
        self,
        point: FontPoint,
        view_box: Tuple[float, float, float, float],
        scale: float,
    ) -> FontPoint:
        """SVG 座標を表示・ロボット処理用のXY座標へ変換する。"""
        view_x_min = view_box[0]
        view_y_min = view_box[1]
        view_height = view_box[3]

        x = (point.x - view_x_min) * scale

        # SVG は下向きが +Y である。
        # 既存の viewer と motion 系では上向きを +Y として扱うため反転する。
        y = (view_height - (point.y - view_y_min)) * scale

        return FontPoint(
            x=x,
            y=y,
        )


class SvgPathSampler:
    """SVG path の M/L/H/V/Q/T/C/S/Z 命令を点列へサンプリングする。"""

    def __init__(
        self,
        curve_division: int,
    ) -> None:
        """曲線命令の分割数を設定する。"""
        if curve_division < 1:
            raise ValueError("curve_division は1以上である必要がある。")

        self._curve_division = curve_division

    def sample_path(
        self,
        path_data: str,
    ) -> List[FontPoint]:
        """SVG path data を点列へ変換する。"""
        tokens = self._tokenize_path(
            path_data=path_data,
        )

        points: List[FontPoint] = []

        current_point = FontPoint(
            x=0.0,
            y=0.0,
        )
        start_point = FontPoint(
            x=0.0,
            y=0.0,
        )

        previous_command = ""
        previous_cubic_control: Optional[FontPoint] = None
        previous_quadratic_control: Optional[FontPoint] = None

        index = 0
        command = ""

        while index < len(tokens):
            token = tokens[index]

            if self._is_command_token(token):
                command = token
                index = index + 1
            elif command == "":
                raise ValueError("SVG path が command 以外から始まっている。")

            command_upper = command.upper()
            relative = command.islower()

            if command_upper == "M":
                first_point = True

                while self._has_number(tokens=tokens, index=index):
                    x = float(tokens[index])
                    y = float(tokens[index + 1])
                    index = index + 2

                    next_point = self._make_point(
                        x=x,
                        y=y,
                        relative=relative,
                        current_point=current_point,
                    )

                    current_point = next_point

                    if first_point:
                        points.append(current_point)
                        start_point = current_point
                        first_point = False
                    else:
                        points.append(current_point)

                previous_cubic_control = None
                previous_quadratic_control = None
                previous_command = command

            elif command_upper == "L":
                while self._has_number(tokens=tokens, index=index):
                    x = float(tokens[index])
                    y = float(tokens[index + 1])
                    index = index + 2

                    current_point = self._make_point(
                        x=x,
                        y=y,
                        relative=relative,
                        current_point=current_point,
                    )
                    points.append(current_point)

                previous_cubic_control = None
                previous_quadratic_control = None
                previous_command = command

            elif command_upper == "H":
                while self._has_number(tokens=tokens, index=index):
                    x = float(tokens[index])
                    index = index + 1

                    if relative:
                        current_point = FontPoint(
                            x=current_point.x + x,
                            y=current_point.y,
                        )
                    else:
                        current_point = FontPoint(
                            x=x,
                            y=current_point.y,
                        )

                    points.append(current_point)

                previous_cubic_control = None
                previous_quadratic_control = None
                previous_command = command

            elif command_upper == "V":
                while self._has_number(tokens=tokens, index=index):
                    y = float(tokens[index])
                    index = index + 1

                    if relative:
                        current_point = FontPoint(
                            x=current_point.x,
                            y=current_point.y + y,
                        )
                    else:
                        current_point = FontPoint(
                            x=current_point.x,
                            y=y,
                        )

                    points.append(current_point)

                previous_cubic_control = None
                previous_quadratic_control = None
                previous_command = command

            elif command_upper == "C":
                while self._has_number(tokens=tokens, index=index):
                    control_1 = self._make_point(
                        x=float(tokens[index]),
                        y=float(tokens[index + 1]),
                        relative=relative,
                        current_point=current_point,
                    )
                    control_2 = self._make_point(
                        x=float(tokens[index + 2]),
                        y=float(tokens[index + 3]),
                        relative=relative,
                        current_point=current_point,
                    )
                    end_point = self._make_point(
                        x=float(tokens[index + 4]),
                        y=float(tokens[index + 5]),
                        relative=relative,
                        current_point=current_point,
                    )
                    index = index + 6

                    curve_points = self._sample_cubic_bezier(
                        p0=current_point,
                        p1=control_1,
                        p2=control_2,
                        p3=end_point,
                    )

                    for point in curve_points:
                        points.append(point)

                    current_point = end_point
                    previous_cubic_control = control_2
                    previous_quadratic_control = None
                    previous_command = command

            elif command_upper == "S":
                while self._has_number(tokens=tokens, index=index):
                    if previous_command.upper() in ["C", "S"]:
                        control_1 = self._reflect_point(
                            point=previous_cubic_control,
                            center=current_point,
                        )
                    else:
                        control_1 = current_point

                    control_2 = self._make_point(
                        x=float(tokens[index]),
                        y=float(tokens[index + 1]),
                        relative=relative,
                        current_point=current_point,
                    )
                    end_point = self._make_point(
                        x=float(tokens[index + 2]),
                        y=float(tokens[index + 3]),
                        relative=relative,
                        current_point=current_point,
                    )
                    index = index + 4

                    curve_points = self._sample_cubic_bezier(
                        p0=current_point,
                        p1=control_1,
                        p2=control_2,
                        p3=end_point,
                    )

                    for point in curve_points:
                        points.append(point)

                    current_point = end_point
                    previous_cubic_control = control_2
                    previous_quadratic_control = None
                    previous_command = command

            elif command_upper == "Q":
                while self._has_number(tokens=tokens, index=index):
                    control = self._make_point(
                        x=float(tokens[index]),
                        y=float(tokens[index + 1]),
                        relative=relative,
                        current_point=current_point,
                    )
                    end_point = self._make_point(
                        x=float(tokens[index + 2]),
                        y=float(tokens[index + 3]),
                        relative=relative,
                        current_point=current_point,
                    )
                    index = index + 4

                    curve_points = self._sample_quadratic_bezier(
                        p0=current_point,
                        p1=control,
                        p2=end_point,
                    )

                    for point in curve_points:
                        points.append(point)

                    current_point = end_point
                    previous_quadratic_control = control
                    previous_cubic_control = None
                    previous_command = command

            elif command_upper == "T":
                while self._has_number(tokens=tokens, index=index):
                    if previous_command.upper() in ["Q", "T"]:
                        control = self._reflect_point(
                            point=previous_quadratic_control,
                            center=current_point,
                        )
                    else:
                        control = current_point

                    end_point = self._make_point(
                        x=float(tokens[index]),
                        y=float(tokens[index + 1]),
                        relative=relative,
                        current_point=current_point,
                    )
                    index = index + 2

                    curve_points = self._sample_quadratic_bezier(
                        p0=current_point,
                        p1=control,
                        p2=end_point,
                    )

                    for point in curve_points:
                        points.append(point)

                    current_point = end_point
                    previous_quadratic_control = control
                    previous_cubic_control = None
                    previous_command = command

            elif command_upper == "Z":
                current_point = start_point
                points.append(current_point)

                previous_cubic_control = None
                previous_quadratic_control = None
                previous_command = command

            else:
                raise ValueError("未対応の SVG path command である: {}".format(command))

        return points

    def _tokenize_path(
        self,
        path_data: str,
    ) -> List[str]:
        """SVG path data を command と数値 token に分解する。"""
        pattern = r"[AaCcHhLlMmQqSsTtVvZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
        return re.findall(pattern, path_data)

    def _is_command_token(
        self,
        token: str,
    ) -> bool:
        """token が SVG path command か判定する。"""
        return bool(re.fullmatch(r"[AaCcHhLlMmQqSsTtVvZz]", token))

    def _has_number(
        self,
        tokens: List[str],
        index: int,
    ) -> bool:
        """現在位置に数値 token があるか判定する。"""
        if index >= len(tokens):
            return False

        return not self._is_command_token(
            token=tokens[index],
        )

    def _make_point(
        self,
        x: float,
        y: float,
        relative: bool,
        current_point: FontPoint,
    ) -> FontPoint:
        """絶対または相対座標から FontPoint を作る。"""
        if relative:
            return FontPoint(
                x=current_point.x + x,
                y=current_point.y + y,
            )

        return FontPoint(
            x=x,
            y=y,
        )

    def _reflect_point(
        self,
        point: Optional[FontPoint],
        center: FontPoint,
    ) -> FontPoint:
        """制御点を現在点に対して反転する。"""
        if point is None:
            return center

        return FontPoint(
            x=2.0 * center.x - point.x,
            y=2.0 * center.y - point.y,
        )

    def _sample_quadratic_bezier(
        self,
        p0: FontPoint,
        p1: FontPoint,
        p2: FontPoint,
    ) -> List[FontPoint]:
        """2次ベジェ曲線を点列化する。"""
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

            points.append(
                FontPoint(
                    x=x,
                    y=y,
                )
            )

        return points

    def _sample_cubic_bezier(
        self,
        p0: FontPoint,
        p1: FontPoint,
        p2: FontPoint,
        p3: FontPoint,
    ) -> List[FontPoint]:
        """3次ベジェ曲線を点列化する。"""
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

            points.append(
                FontPoint(
                    x=x,
                    y=y,
                )
            )

        return points


def main() -> None:
    """KanjiVG stroke 読み込みを単体確認する。"""
    from glyph_motion.lib.run_font_viewer import FontViewer

    loader = FontKanjiVGStrokeLoader(
        kanjivg_directory=Path("kanjivg/kanji"),
        height=40.0,
        spacing=5.0,
        curve_division=16,
    )

    stroke_glyph = loader.load_text(
        text="島",
    )

    print(stroke_glyph)
    print("stroke_count =", len(stroke_glyph))

    viewer = FontViewer()
    viewer.show_stroke(
        stroke_glyph=stroke_glyph,
    )


if __name__ == "__main__":
    main()
