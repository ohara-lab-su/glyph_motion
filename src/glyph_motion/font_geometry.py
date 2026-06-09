from dataclasses import dataclass
from typing import Iterator, List, Tuple


@dataclass
class MeshPoint:
    """メッシュ座標上の一点を表すデータクラスである。

    2次元平面上のX座標およびY座標を保持し、拡大縮小や平行移動の幾何変換機能を提供する。
    """

    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        """座標をタプル形式で返す。

        Returns:
            Tuple[float, float]: (x, y) の座標タプル。
        """
        return self.x, self.y

    def scaled(self, scale: float) -> "MeshPoint":
        """座標を原点を中心に拡大縮小した新しい点を返す。

        Args:
            scale (float): 拡大縮小倍率。

        Returns:
            MeshPoint: 変換後の新しいMeshPointインスタンス。
        """
        return MeshPoint(
            x=self.x * scale,
            y=self.y * scale,
        )

    def shifted(self, x_offset: float, y_offset: float) -> "MeshPoint":
        """座標を指定量だけ平行移動した新しい点を返す。

        Args:
            x_offset (float): X軸方向の移動量。
            y_offset (float): Y軸方向の移動量。

        Returns:
            MeshPoint: 変換後の新しいMeshPointインスタンス。
        """
        return MeshPoint(
            x=self.x + x_offset,
            y=self.y + y_offset,
        )


@dataclass
class MeshPath:
    """一続きの点列で構成されるパスを表すデータクラスである。

    複数のMeshPointを内包し、パスが閉じているかどうかのフラグを保持する。
    """

    points: List[MeshPoint]
    closed: bool

    def __iter__(self) -> Iterator[MeshPoint]:
        """パス内の点列を順に返すイテレータを取得する。

        Returns:
            Iterator[MeshPoint]: 点列のイテレータ。
        """
        return iter(self.points)

    def __len__(self) -> int:
        """パスを構成する点の総数を返す。

        Returns:
            int: 点の数。
        """
        return len(self.points)

    def append(self, point: MeshPoint) -> None:
        """パスの末尾に新しい点を追加する。

        Args:
            point (MeshPoint): 追加する点データ。
        """
        self.points.append(point)

    def scaled(self, scale: float) -> "MeshPath":
        """パス全体を拡大縮小した新しいパスを返す。

        Args:
            scale (float): 拡大縮小倍率。

        Returns:
            MeshPath: 変換後の新しいMeshPathインスタンス。
        """
        points: List[MeshPoint] = []
        for point in self.points:
            points.append(point.scaled(scale=scale))
        return MeshPath(
            points=points,
            closed=self.closed,
        )

    def shifted(self, x_offset: float, y_offset: float) -> "MeshPath":
        """パス全体を平行移動した新しいパスを返す。

        Args:
            x_offset (float): X軸方向の移動量。
            y_offset (float): Y軸方向の移動量。

        Returns:
            MeshPath: 変換後の新しいMeshPathインスタンス。
        """
        points: List[MeshPoint] = []
        for point in self.points:
            points.append(point.shifted(x_offset=x_offset, y_offset=y_offset))
        return MeshPath(
            points=points,
            closed=self.closed,
        )


@dataclass
class GlyphMesh:
    """文字グリフから得た複数のパスで構成されるメッシュ座標群を表すデータクラスである。"""

    paths: List[MeshPath]

    def __iter__(self) -> Iterator[MeshPath]:
        """メッシュ内のパスを順に返すイテレータを取得する。

        Returns:
            Iterator[MeshPath]: パス列のイテレータ。
        """
        return iter(self.paths)

    def __len__(self) -> int:
        """メッシュを構成するパスの総数を返す。

        Returns:
            int: パスの数。
        """
        return len(self.paths)

    def append(self, path: MeshPath) -> None:
        """メッシュに新しいパスを追加する。

        Args:
            path (MeshPath): 追加するパスデータ。
        """
        self.paths.append(path)

    def extend(self, glyph_mesh: "GlyphMesh") -> None:
        """別のGlyphMeshに含まれるすべてのパスを自身に追加して結合する。

        Args:
            glyph_mesh (GlyphMesh): 結合対象のGlyphMeshインスタンス。
        """
        for path in glyph_mesh:
            self.paths.append(path)

    def scaled(self, scale: float) -> "GlyphMesh":
        """メッシュ全体を拡大縮小した新しいメッシュを返す。

        Args:
            scale (float): 拡大縮小倍率。

        Returns:
            GlyphMesh: 変換後の新しいGlyphMeshインスタンス。
        """
        paths: List[MeshPath] = []
        for path in self.paths:
            paths.append(path.scaled(scale=scale))
        return GlyphMesh(paths=paths)

    def shifted(self, x_offset: float, y_offset: float) -> "GlyphMesh":
        """メッシュ全体を平行移動した新しいメッシュを返す。

        Args:
            x_offset (float): X軸方向の移動量。
            y_offset (float): Y軸方向の移動量。

        Returns:
            GlyphMesh: 変換後の新しいGlyphMeshインスタンス。
        """
        paths: List[MeshPath] = []
        for path in self.paths:
            paths.append(path.shifted(x_offset=x_offset, y_offset=y_offset))
        return GlyphMesh(paths=paths)


def main() -> None:
    """GlyphMeshおよび付随する幾何クラスの基本動作を検証する。"""
    path = MeshPath(
        points=[
            MeshPoint(x=0.0, y=0.0),
            MeshPoint(x=10.0, y=0.0),
        ],
        closed=False,
    )

    glyph_mesh = GlyphMesh(
        paths=[path],
    )

    print(glyph_mesh)
    print(glyph_mesh.scaled(scale=2.0))
    print(glyph_mesh.shifted(x_offset=1.0, y_offset=2.0))


if __name__ == "__main__":
    main()