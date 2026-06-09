from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Tuple


@dataclass
class MeshPoint:
    """メッシュ座標上の一点を表すデータである。"""

    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        """座標をタプルで返す。"""
        return self.x, self.y


@dataclass
class MeshPath:
    """一続きの点列で構成されるパスを表すデータである。"""

    points: List[MeshPoint]
    closed: bool

    def __iter__(self) -> Iterator[MeshPoint]:
        """点を順に返す。"""
        return iter(self.points)

    def __len__(self) -> int:
        """点数を返す。"""
        return len(self.points)

    def append(self, point: MeshPoint) -> None:
        """点を追加する。"""
        self.points.append(point)


@dataclass
class GlyphMesh:
    """文字グリフから得たメッシュ座標群を表すデータである。"""

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


def main() -> None:
    point_0 = MeshPoint(
        x=0.0,
        y=0.0,
    )
    point_1 = MeshPoint(
        x=10.0,
        y=0.0,
    )

    mesh_path = MeshPath(
        points=[
            point_0,
            point_1,
        ],
        closed=False,
    )

    glyph_mesh = GlyphMesh(
        paths=[
            mesh_path,
        ],
    )

    print(glyph_mesh)
    print(len(glyph_mesh))
    print(len(mesh_path))


if __name__ == "__main__":
    main()