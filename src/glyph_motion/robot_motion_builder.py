#!/usr/bin/env python
from typing import Dict, List


class RobotMotionBuilder:
    """XY座標列をロボット向けの相対移動列へ変換するクラスである。"""

    def build_relative_motion(
        self,
        contours: Contours,
    ) -> List[Dict[str, float]]:
        """輪郭座標列から相対移動命令列を作る。"""
        commands: List[Dict[str, float]] = []

        current_x = 0.0
        current_y = 0.0

        for contour in contours:
            if len(contour) == 0:
                continue

            start_point = contour[0]
            start_x = start_point[0]
            start_y = start_point[1]

            move_to_start = {
                "pen": 0.0,
                "dx": start_x - current_x,
                "dy": start_y - current_y,
            }
            commands.append(move_to_start)

            current_x = start_x
            current_y = start_y

            pen_down = {
                "pen": 1.0,
                "dx": 0.0,
                "dy": 0.0,
            }
            commands.append(pen_down)

            for point_index in range(1, len(contour)):
                point = contour[point_index]

                next_x = point[0]
                next_y = point[1]

                command = {
                    "pen": 1.0,
                    "dx": next_x - current_x,
                    "dy": next_y - current_y,
                }
                commands.append(command)

                current_x = next_x
                current_y = next_y

            pen_up = {
                "pen": 0.0,
                "dx": 0.0,
                "dy": 0.0,
            }
            commands.append(pen_up)

        return commands

    def rebuild_absolute_points(
        self,
        commands: List[Dict[str, float]],
    ) -> Contours:
        """相対移動命令列を絶対座標列へ戻す。"""
        contours: Contours = []
        current_contour: Contour = []

        current_x = 0.0
        current_y = 0.0
        pen_is_down = False

        for command in commands:
            dx = command["dx"]
            dy = command["dy"]
            pen = command["pen"]

            current_x = current_x + dx
            current_y = current_y + dy

            if pen == 0.0:
                if pen_is_down:
                    if len(current_contour) > 0:
                        contours.append(current_contour)

                    current_contour = []

                pen_is_down = False

            else:
                if not pen_is_down:
                    current_contour = []
                    current_contour.append((current_x, current_y))
                    pen_is_down = True

                else:
                    current_contour.append((current_x, current_y))

        if len(current_contour) > 0:
            contours.append(current_contour)

        return contours
