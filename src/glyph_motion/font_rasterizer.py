#!/usr/bin/env python
from typing import List, Tuple

class FontRasterizer:
    """輪郭線分を一定間隔の点群へ変換するクラスである。"""

    def __init__(
        self,
        step_mm: float,
    ) -> None:
        self._step_mm = step_mm

    def rasterize(
        self,
        contours: Contours,
    ) -> Contours:
        """輪郭座標列を一定間隔の点列へ変換する。"""
        rasterized_contours: Contours = []

        for contour in contours:
            rasterized_contour = self._rasterize_contour(contour)
            rasterized_contours.append(rasterized_contour)

        return rasterized_contours

    def _rasterize_contour(
        self,
        contour: Contour,
    ) -> Contour:
        """1本の輪郭を一定間隔の点列へ変換する。"""
        rasterized_points: Contour = []

        if len(contour) == 0:
            return rasterized_points

        first_point = contour[0]
        rasterized_points.append(first_point)

        for point_index in range(1, len(contour)):
            start_point = contour[point_index - 1]
            end_point = contour[point_index]

            line_points = self._rasterize_line(
                start_point=start_point,
                end_point=end_point,
            )

            for line_point in line_points:
                rasterized_points.append(line_point)

        return rasterized_points

    def _rasterize_line(
        self,
        start_point: Point2D,
        end_point: Point2D,
    ) -> Contour:
        """1本の線分を一定間隔の点列へ変換する。"""
        x0 = start_point[0]
        y0 = start_point[1]
        x1 = end_point[0]
        y1 = end_point[1]

        dx = x1 - x0
        dy = y1 - y0

        distance = (dx * dx + dy * dy) ** 0.5

        if distance == 0.0:
            return []

        division_count = int(distance / self._step_mm)

        if division_count < 1:
            division_count = 1

        points: Contour = []

        for division_index in range(1, division_count + 1):
            ratio = float(division_index) / float(division_count)

            x = x0 + dx * ratio
            y = y0 + dy * ratio

            points.append((x, y))

        return points

