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

    def scaled(
        self,
        scale: float,
    ) -> "MeshPoint":
        """座標を拡大縮小した点を返す。"""
        return MeshPoint(
            x=self.x * scale,
            y=self.y * scale,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "MeshPoint":
        """座標を平行移動した点を返す。"""
        return MeshPoint(
            x=self.x + x_offset,
            y=self.y + y_offset,
        )


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

    def append(
        self,
        point: MeshPoint,
    ) -> None:
        """点を追加する。"""
        self.points.append(point)

    def scaled(
        self,
        scale: float,
    ) -> "MeshPath":
        """パス全体を拡大縮小したパスを返す。"""
        points: List[MeshPoint] = []

        for point in self.points:
            points.append(
                point.scaled(
                    scale=scale,
                )
            )

        return MeshPath(
            points=points,
            closed=self.closed,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "MeshPath":
        """パス全体を平行移動したパスを返す。"""
        points: List[MeshPoint] = []

        for point in self.points:
            points.append(
                point.shifted(
                    x_offset=x_offset,
                    y_offset=y_offset,
                )
            )

        return MeshPath(
            points=points,
            closed=self.closed,
        )


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

    def append(
        self,
        path: MeshPath,
    ) -> None:
        """パスを追加する。"""
        self.paths.append(path)

    def extend(
        self,
        glyph_mesh: "GlyphMesh",
    ) -> None:
        """別のGlyphMeshに含まれるパスを追加する。"""
        for path in glyph_mesh:
            self.paths.append(path)

    def scaled(
        self,
        scale: float,
    ) -> "GlyphMesh":
        """GlyphMesh全体を拡大縮小したGlyphMeshを返す。"""
        paths: List[MeshPath] = []

        for path in self.paths:
            paths.append(
                path.scaled(
                    scale=scale,
                )
            )

        return GlyphMesh(
            paths=paths,
        )

    def shifted(
        self,
        x_offset: float,
        y_offset: float,
    ) -> "GlyphMesh":
        """GlyphMesh全体を平行移動したGlyphMeshを返す。"""
        paths: List[MeshPath] = []

        for path in self.paths:
            paths.append(
                path.shifted(
                    x_offset=x_offset,
                    y_offset=y_offset,
                )
            )

        return GlyphMesh(
            paths=paths,
        )


def main() -> None:
    path = MeshPath(
        points=[
            MeshPoint(
                x=0.0,
                y=0.0,
            ),
            MeshPoint(
                x=10.0,
                y=0.0,
            ),
        ],
        closed=False,
    )

    glyph_mesh = GlyphMesh(
        paths=[
            path,
        ],
    )

    print(glyph_mesh)
    print(glyph_mesh.scaled(scale=2.0))
    print(glyph_mesh.shifted(x_offset=1.0, y_offset=2.0))


if __name__ == "__main__":
    main()