#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

中心線抽出後の線分を、ロボット移動命令へ渡しやすい点列へ整理する。

FontCenterlineExtractor が出力する FontCenterlineGlyph は、画像処理で得た
生の中心線である。生の中心線には、短い枝、重複点、細かすぎる点間隔、
孤立した短線分が含まれる可能性がある。

このモジュールは、生の FontCenterlineGlyph を入力として受け取り、
短すぎる線分の除去、連続重複点の除去、点間隔の再サンプリングを行った
FontCenterlineGlyph を返す。

ここではフォント読み込み、輪郭抽出、塗りつぶし、中心線抽出、表示、
ロボット固有API呼び出しは行わない。
"""

from typing import List

from font_geometry import FontCenterlineGlyph
from font_geometry import FontCenterlinePath
from font_geometry import FontPoint


class FontCenterlineCleaner:
    """生の中心線をロボット向けの中心線へ整理するクラスである。"""

    def __init__(
        self,
        min_path_length: float,
        point_spacing: float,
    ) -> None:
        """中心線整理条件を設定する。

        Args:
            min_path_length: この長さ未満の中心線パスを除去する。
            point_spacing: 再サンプリング後の目標点間隔である。
        """
        if min_path_length < 0.0:
            raise ValueError("min_path_length は0以上である必要がある。")

        if point_spacing <= 0.0:
            raise ValueError("point_spacing は正の値である必要がある。")

        self._min_path_length = min_path_length
        self._point_spacing = point_spacing

    def clean(
        self,
        centerline_glyph: FontCenterlineGlyph,
    ) -> FontCenterlineGlyph:
        """中心線群を整理する。

        Args:
            centerline_glyph: 整理対象の中心線群である。

        Returns:
            FontCenterlineGlyph: 整理後の中心線群である。
        """
        cleaned_paths: List[FontCenterlinePath] = []

        for centerline_path in centerline_glyph:
            unique_path = self._remove_consecutive_duplicate_points(
                centerline_path=centerline_path,
            )

            path_length = self._calculate_path_length(
                centerline_path=unique_path,
            )

            if path_length < self._min_path_length:
                continue

            resampled_path = self._resample_path(
                centerline_path=unique_path,
            )

            if len(resampled_path) < 2:
                continue

            cleaned_paths.append(resampled_path)

        return FontCenterlineGlyph(
            text=centerline_glyph.text,
            paths=cleaned_paths,
        )

    def _remove_consecutive_duplicate_points(
        self,
        centerline_path: FontCenterlinePath,
    ) -> FontCenterlinePath:
        """連続する同一点を除去する。"""
        points: List[FontPoint] = []

        previous_point = None

        for point in centerline_path:
            if previous_point is None:
                points.append(point)
                previous_point = point
                continue

            distance = self._calculate_distance(
                point_a=previous_point,
                point_b=point,
            )

            if distance == 0.0:
                continue

            points.append(point)
            previous_point = point

        return FontCenterlinePath(
            points=points,
        )

    def _calculate_path_length(
        self,
        centerline_path: FontCenterlinePath,
    ) -> float:
        """中心線パス全体の長さを計算する。"""
        total_length = 0.0

        if len(centerline_path) < 2:
            return total_length

        for point_index in range(1, len(centerline_path.points)):
            previous_point = centerline_path.points[point_index - 1]
            current_point = centerline_path.points[point_index]

            total_length = total_length + self._calculate_distance(
                point_a=previous_point,
                point_b=current_point,
            )

        return total_length

    def _resample_path(
        self,
        centerline_path: FontCenterlinePath,
    ) -> FontCenterlinePath:
        """中心線パスを指定間隔に近い点列へ再サンプリングする。"""
        if len(centerline_path) < 2:
            return FontCenterlinePath(
                points=centerline_path.points,
            )

        resampled_points: List[FontPoint] = [
            centerline_path.points[0],
        ]

        carry_distance = 0.0
        segment_start = centerline_path.points[0]

        for point_index in range(1, len(centerline_path.points)):
            segment_end = centerline_path.points[point_index]

            segment_length = self._calculate_distance(
                point_a=segment_start,
                point_b=segment_end,
            )

            if segment_length == 0.0:
                segment_start = segment_end
                continue

            distance_from_start = self._point_spacing - carry_distance

            while distance_from_start <= segment_length:
                ratio = distance_from_start / segment_length

                new_point = FontPoint(
                    x=segment_start.x + (segment_end.x - segment_start.x) * ratio,
                    y=segment_start.y + (segment_end.y - segment_start.y) * ratio,
                )

                resampled_points.append(new_point)

                distance_from_start = distance_from_start + self._point_spacing

            used_distance = distance_from_start - self._point_spacing
            carry_distance = segment_length - used_distance
            segment_start = segment_end

        last_point = centerline_path.points[-1]
        previous_point = resampled_points[-1]

        last_distance = self._calculate_distance(
            point_a=previous_point,
            point_b=last_point,
        )

        if last_distance > 0.0:
            resampled_points.append(last_point)

        return FontCenterlinePath(
            points=resampled_points,
        )

    def _calculate_distance(
        self,
        point_a: FontPoint,
        point_b: FontPoint,
    ) -> float:
        """2点間距離を返す。"""
        dx = point_b.x - point_a.x
        dy = point_b.y - point_a.y

        return (dx * dx + dy * dy) ** 0.5


def main() -> None:
    """中心線整理を単体確認する。"""
    from font_geometry import FontCenterlineGlyph
    from font_geometry import FontCenterlinePath
    from font_viewer import FontViewer

    centerline = FontCenterlineGlyph(
        text="test",
        paths=[
            FontCenterlinePath(
                points=[
                    FontPoint(x=0.0, y=0.0),
                    FontPoint(x=0.0, y=0.0),
                    FontPoint(x=10.0, y=0.0),
                    FontPoint(x=10.0, y=10.0),
                ],
            ),
            FontCenterlinePath(
                points=[
                    FontPoint(x=1.0, y=1.0),
                    FontPoint(x=1.1, y=1.0),
                ],
            ),
        ],
    )

    cleaner = FontCenterlineCleaner(
        min_path_length=1.0,
        point_spacing=2.0,
    )

    cleaned = cleaner.clean(
        centerline_glyph=centerline,
    )

    print(cleaned)

    viewer = FontViewer()
    viewer.show_centerline(
        centerline_glyph=cleaned,
    )


if __name__ == "__main__":
    main()
