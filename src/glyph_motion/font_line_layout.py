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
        character,
        index,
        cell_origin_x,
        cell_origin_y,
        strokes,
    ):
        # type: (str, int, float, float, List[FontStrokePath]) -> None
        self.character = character
        self.index = index
        self.cell_origin_x = float(cell_origin_x)
        self.cell_origin_y = float(cell_origin_y)
        self.strokes = strokes


class FontLineLayout:
    """固定作業空間内に、一行分の文字ストロークを配置する。"""

    def __init__(
        self,
        kanjivg_directory,
        workspace_width,
        workspace_height,
        cell_width,
        cell_height,
        character_height,
        curve_division=16,
    ):
        # type: (Path, float, float, float, float, float, int) -> None
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

        self._loader = FontKanjiVGStrokeLoader(
            kanjivg_directory=kanjivg_directory,
            height=self.character_height,
            spacing=0.0,
            curve_division=curve_division,
        )

    @property
    def capacity(self):
        # type: () -> int
        return int(self.workspace_width // self.cell_width)

    def build(self, text):
        # type: (str) -> List[PositionedCharacter]
        """一行の文字列を固定文字空間へ配置する。"""
        if len(text) > self.capacity:
            raise ValueError(
                "文字数が作業空間の収容数を超えている: {} > {}".format(
                    len(text),
                    self.capacity,
                )
            )

        positioned_characters = []  # type: List[PositionedCharacter]

        for character_index, character in enumerate(text):
            cell_origin_x = float(character_index) * self.cell_width
            cell_origin_y = 0.0

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

            strokes = []  # type: List[FontStrokePath]
            for stroke in character_glyph:
                points = []  # type: List[FontPoint]
                for point in stroke:
                    points.append(
                        FontPoint(
                            x=point.x + x_offset,
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
