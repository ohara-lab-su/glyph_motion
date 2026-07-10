#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
固定された一行の作業空間へ、KanjiVG の各文字を配置する。

このモジュールはロボット制御を行わない。
文字列を、文字ごとの固定文字空間に配置された FontStrokePath 群へ変換する。
"""

from pathlib import Path
from typing import List

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokePath
from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader


class PositionedCharacter:
    """一つの文字空間へ配置済みの文字ストロークを保持する。"""

    def __init__(
        self,
        character: str,
        index: int,
        cell_origin_x: float,
        cell_origin_y: float,
        strokes: List[FontStrokePath],
    ) -> None:
        self.character = character
        self.index = index
        self.cell_origin_x = float(cell_origin_x)
        self.cell_origin_y = float(cell_origin_y)
        self.strokes = strokes


class FontLineLayout:
    """固定作業空間内に、一行分の文字ストロークを配置する。"""

    def __init__(
        self,
        kanjivg_directory: Path,
        workspace_width: float,
        workspace_height: float,
        cell_width: float,
        cell_height: float,
        character_height: float,
        curve_division: int = 16,
        line_direction: str = "left_to_right",
        writing_direction: str = "horizontal",
        mirror_horizontal: bool = False,
        mirror_vertical: bool = False,
    ) -> None:
        if workspace_width <= 0.0:
            raise ValueError("workspace_width は正の値である必要がある。")
        if workspace_height <= 0.0:
            raise ValueError("workspace_height は正の値である必要がある。")
        if cell_width <= 0.0:
            raise ValueError("cell_width は正の値である必要がある。")
        if cell_height <= 0.0:
            raise ValueError("cell_height は正の値である必要がある。")
        if character_height <= 0.0:
            raise ValueError("character_height は正の値である必要がある。")
        if character_height > cell_height:
            raise ValueError("character_height は cell_height 以下である必要がある。")

        self.workspace_width = float(workspace_width)
        self.workspace_height = float(workspace_height)
        self.cell_width = float(cell_width)
        self.cell_height = float(cell_height)
        self.character_height = float(character_height)

        if line_direction not in ("left_to_right", "right_to_left"):
            raise ValueError(
                "line_direction は left_to_right または right_to_left を指定してください。"
            )

        self.line_direction = line_direction
        if writing_direction not in ("horizontal","vertical"):
            raise ValueError("writing_direction must be horizontal or vertical")
        self.writing_direction = writing_direction
        self.mirror_horizontal = bool(mirror_horizontal)
        self.mirror_vertical = bool(mirror_vertical)

        self._loader = FontKanjiVGStrokeLoader(
            kanjivg_directory=kanjivg_directory,
            height=self.character_height,
            spacing=0.0,
            curve_division=curve_division,
        )

    @property
    def capacity(self) -> int:
        return int(self.workspace_width // self.cell_width)

    def build(
        self,
        text: str,
    ) -> List[PositionedCharacter]:
        """一行の文字列を固定文字空間へ配置する。"""
        if len(text) > self.capacity:
            raise ValueError(
                "文字数が作業空間の収容数を超えている: {} > {}".format(
                    len(text),
                    self.capacity,
                )
            )

        positioned_characters = []

        for character_index, character in enumerate(text):
            if self.line_direction == "left_to_right":
                cell_index = character_index
            else:
                cell_index = self.capacity - 1 - character_index

            if self.writing_direction == "horizontal":
                cell_origin_x = float(cell_index) * self.cell_width
                cell_origin_y = 0.0
            else:
                cell_origin_x = 0.0
                cell_origin_y = float(cell_index) * self.cell_height

            if character == " ":
                positioned_characters.append(
                    PositionedCharacter(
                        character=character,
                        index=character_index,
                        cell_origin_x=cell_origin_x,
                        cell_origin_y=cell_origin_y,
                        strokes=[],
                    )
                )
                continue

            character_glyph, advance_width = self._loader.load_character(
                character=character,
            )

            if advance_width > self.cell_width:
                raise ValueError(
                    "文字幅が文字空間を超えている: {}: {} > {}".format(
                        character,
                        advance_width,
                        self.cell_width,
                    )
                )

            x_offset = cell_origin_x + (self.cell_width - advance_width) / 2.0
            y_offset = cell_origin_y + (self.cell_height - self.character_height) / 2.0

            strokes = []
            for stroke in character_glyph:
                points = []
                for point in stroke:
                    positioned_x = point.x + x_offset

                    if self.mirror_horizontal:
                        local_x = positioned_x - cell_origin_x
                        positioned_x = cell_origin_x + self.cell_width - local_x

                    points.append(
                        FontPoint(
                            x=positioned_x,
                            y=point.y + y_offset,
                        )
                    )

                if len(points) > 0:
                    strokes.append(FontStrokePath(points=points))

            positioned_characters.append(
                PositionedCharacter(
                    character=character,
                    index=character_index,
                    cell_origin_x=cell_origin_x,
                    cell_origin_y=cell_origin_y,
                    strokes=strokes,
                )
            )

        return positioned_characters
