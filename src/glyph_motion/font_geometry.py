from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Tuple


@dataclass
class MeshPoint:
    """メッシュ上の一点を表すデータである。"""

    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        """座標をタプルとして返す。"""
        return self.x, self.y


@dataclass
class MeshPath:
    """一続きのメッシュ点列を表すデータである。"""

    points: List[MeshPoint]
    closed: bool

    def __iter__(self) -> Iterator[MeshPoint]:
        """メッシュ点を順に返す。"""
        return iter(self.points)

    def __len__(self) -> int:
        """メッシュ点数を返す。"""
        return len(self.points)

    def append(self, point: MeshPoint) -> None:
        """メッシュ点を追加する。"""
        self.points.append(point)


@dataclass
class GlyphMesh:
    """一文字または文字列に対応するメッシュ座標群を表すデータである。"""

    paths: List[MeshPath]

    def __iter__(self) -> Iterator[MeshPath]:
        """パスを順に返す。"""
        return iter(self.paths)

    def __len__(self) -> int:
        """パス数を返す。"""
        return len(self.paths)

    def append(self, path: MeshPath) -> None:
        """パスを追加する。"""
        self.paths.append(path)
