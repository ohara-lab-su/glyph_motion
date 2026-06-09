"""
塗りつぶし済み文字領域から中心線を抽出する。

このモジュールは FontFilledGlyph を入力として受け取り、
FontCenterlineGlyph を出力する。

太さを持つ文字領域を細い線へ変換する処理を担当する。
フォント読み込み、輪郭抽出、塗りつぶし、表示、移動命令生成は行わない。
"""

from typing import Dict
from typing import List
from typing import Set
from typing import Tuple

from skimage.morphology import skeletonize

from font_geometry import FontCenterlineGlyph
from font_geometry import FontCenterlinePath
from font_geometry import FontFilledGlyph
from font_geometry import FontPoint


PixelIndex = Tuple[int, int]
PixelEdge = Tuple[PixelIndex, PixelIndex]


class FontCenterlineExtractor:
    """塗りつぶし済み文字領域から中心線を抽出するクラスである。"""

    def extract(
        self,
        filled_glyph: FontFilledGlyph,
    ) -> FontCenterlineGlyph:
        """文字領域から中心線群を抽出する。"""
        skeleton = skeletonize(filled_glyph.mask)

        graph = self._build_graph(
            skeleton=skeleton,
        )

        pixel_paths = self._trace_pixel_paths(
            graph=graph,
        )

        centerline_paths: List[FontCenterlinePath] = []

        for pixel_path in pixel_paths:
            points: List[FontPoint] = []

            for pixel_index in pixel_path:
                row_index = pixel_index[0]
                column_index = pixel_index[1]

                points.append(
                    filled_glyph.index_to_point(
                        row_index=row_index,
                        column_index=column_index,
                    )
                )

            if len(points) > 0:
                centerline_paths.append(
                    FontCenterlinePath(
                        points=points,
                    )
                )

        return FontCenterlineGlyph(
            text=filled_glyph.text,
            paths=centerline_paths,
        )

    def _build_graph(
        self,
        skeleton,
    ) -> Dict[PixelIndex, List[PixelIndex]]:
        """スケルトン画像を8近傍グラフへ変換する。"""
        graph: Dict[PixelIndex, List[PixelIndex]] = {}

        row_count = skeleton.shape[0]
        column_count = skeleton.shape[1]

        for row_index in range(row_count):
            for column_index in range(column_count):
                if skeleton[row_index, column_index] is False:
                    continue

                pixel = (
                    row_index,
                    column_index,
                )

                graph[pixel] = self._collect_neighbors(
                    skeleton=skeleton,
                    row_index=row_index,
                    column_index=column_index,
                )

        return graph

    def _collect_neighbors(
        self,
        skeleton,
        row_index: int,
        column_index: int,
    ) -> List[PixelIndex]:
        """指定ピクセルに隣接するスケルトンピクセルを集める。"""
        neighbors: List[PixelIndex] = []

        row_count = skeleton.shape[0]
        column_count = skeleton.shape[1]

        for d_row in range(-1, 2):
            for d_column in range(-1, 2):
                if d_row == 0:
                    if d_column == 0:
                        continue

                neighbor_row = row_index + d_row
                neighbor_column = column_index + d_column

                if neighbor_row < 0:
                    continue

                if neighbor_column < 0:
                    continue

                if neighbor_row >= row_count:
                    continue

                if neighbor_column >= column_count:
                    continue

                if skeleton[neighbor_row, neighbor_column] is False:
                    continue

                neighbors.append(
                    (
                        neighbor_row,
                        neighbor_column,
                    )
                )

        return neighbors

    def _trace_pixel_paths(
        self,
        graph: Dict[PixelIndex, List[PixelIndex]],
    ) -> List[List[PixelIndex]]:
        """スケルトングラフを線分パス群へ分解する。"""
        paths: List[List[PixelIndex]] = []
        visited_edges: Set[PixelEdge] = set()

        start_pixels = self._collect_start_pixels(
            graph=graph,
        )

        for start_pixel in start_pixels:
            neighbors = graph[start_pixel]

            for neighbor in neighbors:
                edge = self._make_edge(
                    pixel_a=start_pixel,
                    pixel_b=neighbor,
                )

                if edge in visited_edges:
                    continue

                path = self._trace_from_edge(
                    graph=graph,
                    start_pixel=start_pixel,
                    next_pixel=neighbor,
                    visited_edges=visited_edges,
                )

                if len(path) > 1:
                    paths.append(path)

        for pixel in graph:
            neighbors = graph[pixel]

            for neighbor in neighbors:
                edge = self._make_edge(
                    pixel_a=pixel,
                    pixel_b=neighbor,
                )

                if edge in visited_edges:
                    continue

                path = self._trace_from_edge(
                    graph=graph,
                    start_pixel=pixel,
                    next_pixel=neighbor,
                    visited_edges=visited_edges,
                )

                if len(path) > 1:
                    paths.append(path)

        return paths

    def _collect_start_pixels(
        self,
        graph: Dict[PixelIndex, List[PixelIndex]],
    ) -> List[PixelIndex]:
        """線分追跡の始点候補を集める。"""
        start_pixels: List[PixelIndex] = []

        for pixel in graph:
            degree = len(graph[pixel])

            if degree != 2:
                start_pixels.append(pixel)

        if len(start_pixels) == 0:
            for pixel in graph:
                start_pixels.append(pixel)
                break

        return start_pixels

    def _trace_from_edge(
        self,
        graph: Dict[PixelIndex, List[PixelIndex]],
        start_pixel: PixelIndex,
        next_pixel: PixelIndex,
        visited_edges: Set[PixelEdge],
    ) -> List[PixelIndex]:
        """始点と次点から1本の中心線パスを追跡する。"""
        path: List[PixelIndex] = [
            start_pixel,
        ]

        previous_pixel = start_pixel
        current_pixel = next_pixel

        while True:
            edge = self._make_edge(
                pixel_a=previous_pixel,
                pixel_b=current_pixel,
            )

            if edge in visited_edges:
                break

            visited_edges.add(edge)
            path.append(current_pixel)

            neighbors = graph[current_pixel]

            if len(neighbors) != 2:
                break

            candidate_pixels: List[PixelIndex] = []

            for neighbor in neighbors:
                if neighbor != previous_pixel:
                    candidate_pixels.append(neighbor)

            if len(candidate_pixels) == 0:
                break

            previous_pixel = current_pixel
            current_pixel = candidate_pixels[0]

        return path

    def _make_edge(
        self,
        pixel_a: PixelIndex,
        pixel_b: PixelIndex,
    ) -> PixelEdge:
        """無向エッジを一意な順序で表す。"""
        if pixel_a <= pixel_b:
            return (
                pixel_a,
                pixel_b,
            )

        return (
            pixel_b,
            pixel_a,
        )


def main() -> None:
    """中心線抽出を単体確認する。"""
    from pathlib import Path

    from font_fill_glyph import FontGlyphFiller
    from font_outline_extractor import FontOutlineExtractor
    from font_viewer import FontViewer

    font_file = Path("NotoSansCJKjp-Regular.otf")

    if font_file.exists() is False:
        print("NotoSansCJKjp-Regular.otf が見つからない。")
        return

    outline_extractor = FontOutlineExtractor(
        font_file=font_file,
        height=40.0,
        curve_division=8,
    )

    outline = outline_extractor.extract_text(
        text="島",
        spacing=5.0,
    )

    filler = FontGlyphFiller(
        pixel_size=0.5,
        margin=2.0,
    )

    filled = filler.fill(
        outline_glyph=outline,
    )

    centerline_extractor = FontCenterlineExtractor()
    centerline = centerline_extractor.extract(
        filled_glyph=filled,
    )

    viewer = FontViewer()
    viewer.show_filled_with_centerline(
        filled_glyph=filled,
        centerline_glyph=centerline,
    )


if __name__ == "__main__":
    main()