#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

フォント文字を中心線へ変換する処理で共有する幾何データ型を定義する。

このモジュールは、処理段階の入出力データだけを保持する。
フォントの読み込み、輪郭抽出、塗りつぶし、中心線抽出、表示、移動命令生成は
それぞれ別モジュールで行う。
"""

from dataclasses import dataclass
from typing import Iterator, List, Tuple

import numpy as np


@dataclass
class FontPoint:
    """XY平面上の一点を表す。"""

    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        """座標をタプルとして返す。"""
        return self.x, self.y

    def scaled(self, scale: float) -> "FontPoint":
        """原点基準で拡大縮小した点を返す。"""
        return FontPoint(
            x=self.x * scale,
            y=self.y * scale,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "FontPoint":
        """指定量だけ平行移動した点を返す。"""
        return FontPoint(
            x=self.x + x_offset,
            y=self.y + y_offset,
        )


@dataclass
class FontOutlinePath:
    """フォントから取り出した一本の輪郭線を表す。"""

    points: List[FontPoint]
    closed: bool

    def __iter__(self) -> Iterator[FontPoint]:
        """輪郭上の点を順に返す。"""
        return iter(self.points)

    def __len__(self) -> int:
        """輪郭点数を返す。"""
        return len(self.points)

    def scaled(self, scale: float) -> "FontOutlinePath":
        """輪郭全体を拡大縮小した輪郭を返す。"""
        points: List[FontPoint] = []

        for point in self.points:
            points.append(point.scaled(scale=scale))

        return FontOutlinePath(
            points=points,
            closed=self.closed,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "FontOutlinePath":
        """輪郭全体を平行移動した輪郭を返す。"""
        points: List[FontPoint] = []

        for point in self.points:
            points.append(
                point.shifted(
                    x_offset=x_offset,
                    y_offset=y_offset,
                )
            )

        return FontOutlinePath(
            points=points,
            closed=self.closed,
        )


@dataclass
class FontOutlineGlyph:
    """指定文字列から取り出した輪郭線群を表す。"""

    text: str
    paths: List[FontOutlinePath]

    def __iter__(self) -> Iterator[FontOutlinePath]:
        """輪郭線を順に返す。"""
        return iter(self.paths)

    def __len__(self) -> int:
        """輪郭線数を返す。"""
        return len(self.paths)

    def scaled(self, scale: float) -> "FontOutlineGlyph":
        """輪郭線群全体を拡大縮小した文字輪郭を返す。"""
        paths: List[FontOutlinePath] = []

        for path in self.paths:
            paths.append(path.scaled(scale=scale))

        return FontOutlineGlyph(
            text=self.text,
            paths=paths,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "FontOutlineGlyph":
        """輪郭線群全体を平行移動した文字輪郭を返す。"""
        paths: List[FontOutlinePath] = []

        for path in self.paths:
            paths.append(
                path.shifted(
                    x_offset=x_offset,
                    y_offset=y_offset,
                )
            )

        return FontOutlineGlyph(
            text=self.text,
            paths=paths,
        )


@dataclass
class FontFilledGlyph:
    """輪郭を格子上に塗りつぶした文字領域を表す。"""

    text: str
    mask: np.ndarray
    x_min: float
    y_min: float
    pixel_size: float

    def index_to_point(
        self,
        row_index: int,
        column_index: int,
    ) -> FontPoint:
        """配列インデックスをXY座標へ変換する。"""
        x = self.x_min + float(column_index) * self.pixel_size
        y = self.y_min + float(row_index) * self.pixel_size

        return FontPoint(
            x=x,
            y=y,
        )


@dataclass
class FontCenterlinePath:
    """中心線一本を表す。"""

    points: List[FontPoint]

    def __iter__(self) -> Iterator[FontPoint]:
        """中心線上の点を順に返す。"""
        return iter(self.points)

    def __len__(self) -> int:
        """中心線上の点数を返す。"""
        return len(self.points)


@dataclass
class FontCenterlineGlyph:
    """指定文字列から得た中心線群を表す。"""

    text: str
    paths: List[FontCenterlinePath]

    def __iter__(self) -> Iterator[FontCenterlinePath]:
        """中心線を順に返す。"""
        return iter(self.paths)

    def __len__(self) -> int:
        """中心線数を返す。"""
        return len(self.paths)


@dataclass
class FontStrokePath:
    """一回ペンを下ろして書く一本の筆画を表す。

    FontCenterlinePath は、画像処理で抽出された中心線である。
    FontStrokePath は、ロボットが実際に一筆でなぞる単位である。

    paths の分割は、ペンアップ・ペンダウンの単位に対応する。
    """

    points: List[FontPoint]

    def __iter__(self) -> Iterator[FontPoint]:
        """筆画上の点を順に返す。"""
        return iter(self.points)

    def __len__(self) -> int:
        """筆画上の点数を返す。"""
        return len(self.points)


@dataclass
class FontStrokeGlyph:
    """筆順付き文字データを表す。

    paths の順序が、そのままロボットに書かせる順序である。
    各 FontStrokePath は、一回ペンを下ろして書く単位である。
    """

    text: str
    paths: List[FontStrokePath]

    def __iter__(self) -> Iterator[FontStrokePath]:
        """筆画を筆順通りに返す。"""
        return iter(self.paths)

    def __len__(self) -> int:
        """筆画数を返す。"""
        return len(self.paths)


@dataclass
class FontMotionCommand:
    """中心線または筆画から作成したXY相対移動命令を表す。"""

    pen: float
    dx: float
    dy: float


def main() -> None:
    """共通データ型の生成を確認する。"""
    stroke_glyph = FontStrokeGlyph(
        text="A",
        paths=[
            FontStrokePath(
                points=[
                    FontPoint(x=0.0, y=0.0),
                    FontPoint(x=10.0, y=20.0),
                ],
            ),
            FontStrokePath(
                points=[
                    FontPoint(x=10.0, y=20.0),
                    FontPoint(x=20.0, y=0.0),
                ],
            ),
            FontStrokePath(
                points=[
                    FontPoint(x=5.0, y=10.0),
                    FontPoint(x=15.0, y=10.0),
                ],
            ),
        ],
    )

    print(stroke_glyph)
    print(len(stroke_glyph))


if __name__ == "__main__":
    main()
