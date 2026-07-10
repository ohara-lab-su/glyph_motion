#!/usr/bin/env python
"""
K.NAKADA, kengo.nakada@gmail.com

-----------------------------------
font_bcap_cobotta_writer.py
COBOTTA b-CAP を用いて筆順付き文字を書く制御クラスを定義する。
    ↓
font_robot_writer.py
文字列をロボット筆記用の相対移動命令へ変換する簡易 I/F を定義する。
    ↓
font_robot_motion_builder.py
筆順付き stroke データを、ロボット向けの相対移動命令へ変換する。
    ↓
font_motion_builder.py
中心線データまたは筆順付き stroke データをXY相対移動命令へ変換する。
-----------------------------------

筆順付き stroke データを、ロボット向けの相対移動命令へ変換する。

このモジュールは FontStrokeGlyph を入力として受け取り、
Z 上げ下げを含む FontRobotMotionCommand の列を生成する。

ここではロボット固有 API は呼ばない。
このモジュールの出力は、後段のロボット制御クラス、サーバー、gRPC クライアント、
FastAPI I/F などへ渡すための中間命令である。
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from glyph_motion.lib.font_geometry import FontPoint
from glyph_motion.lib.font_geometry import FontStrokeGlyph


@dataclass
class FontRobotMotionCommand:
    """ロボット向けの相対移動命令を表す。

    dx, dy, dz は現在位置からの相対移動量である。

    pen_down が True の命令は、筆記状態での移動である。
    pen_down が False の命令は、非筆記状態での移動である。

    stroke_index は筆画番号である。
    point_index は、その筆画内の点番号である。
    """

    dx: float
    dy: float
    dz: float
    pen_down: bool
    stroke_index: int
    point_index: int
    speed: Optional[float]


class FontRobotMotionBuilder:
    """FontStrokeGlyph からロボット向け相対移動命令列を作る。"""

    def __init__(
        self,
        pen_lift_height: float,
        drawing_speed: Optional[float] = None,
        travel_speed: Optional[float] = None,
    ) -> None:
        """ペン上げ高さと速度条件を設定する。"""
        if pen_lift_height <= 0.0:
            raise ValueError("pen_lift_height は正の値である必要がある。")

        self._pen_lift_height = pen_lift_height
        self._drawing_speed = drawing_speed
        self._travel_speed = travel_speed

    def build(
        self,
        stroke_glyph: FontStrokeGlyph,
    ) -> List[FontRobotMotionCommand]:
        """筆順付き stroke から相対移動命令列を生成する。

        各 stroke は、一回ペンを下ろして書く単位である。
        stroke が変わるたびに、Z 方向へペンを上げ、次の stroke 始点へ移動し、
        Z 方向へペンを下げてから stroke 内をなぞる。
        """
        commands: List[FontRobotMotionCommand] = []

        current_point = FontPoint(
            x=0.0,
            y=0.0,
        )
        current_z = 0.0

        for stroke_index, stroke_path in enumerate(stroke_glyph):
            if len(stroke_path) == 0:
                continue

            start_point = stroke_path.points[0]

            if current_z == 0.0:
                commands.append(
                    self._make_command(
                        dx=0.0,
                        dy=0.0,
                        dz=self._pen_lift_height,
                        pen_down=False,
                        stroke_index=stroke_index,
                        point_index=0,
                        speed=self._travel_speed,
                    )
                )
                current_z = self._pen_lift_height

            commands.append(
                self._make_command(
                    dx=start_point.x - current_point.x,
                    dy=start_point.y - current_point.y,
                    dz=0.0,
                    pen_down=False,
                    stroke_index=stroke_index,
                    point_index=0,
                    speed=self._travel_speed,
                )
            )
            current_point = start_point

            commands.append(
                self._make_command(
                    dx=0.0,
                    dy=0.0,
                    dz=-current_z,
                    pen_down=True,
                    stroke_index=stroke_index,
                    point_index=0,
                    speed=self._drawing_speed,
                )
            )
            current_z = 0.0

            for point_index in range(1, len(stroke_path.points)):
                next_point = stroke_path.points[point_index]

                commands.append(
                    self._make_command(
                        dx=next_point.x - current_point.x,
                        dy=next_point.y - current_point.y,
                        dz=0.0,
                        pen_down=True,
                        stroke_index=stroke_index,
                        point_index=point_index,
                        speed=self._drawing_speed,
                    )
                )
                current_point = next_point

            commands.append(
                self._make_command(
                    dx=0.0,
                    dy=0.0,
                    dz=self._pen_lift_height,
                    pen_down=False,
                    stroke_index=stroke_index,
                    point_index=len(stroke_path.points) - 1,
                    speed=self._travel_speed,
                )
            )
            current_z = self._pen_lift_height

        return commands

    def _make_command(
        self,
        dx: float,
        dy: float,
        dz: float,
        pen_down: bool,
        stroke_index: int,
        point_index: int,
        speed: Optional[float],
    ) -> FontRobotMotionCommand:
        """FontRobotMotionCommand を生成する。"""
        return FontRobotMotionCommand(
            dx=dx,
            dy=dy,
            dz=dz,
            pen_down=pen_down,
            stroke_index=stroke_index,
            point_index=point_index,
            speed=speed,
        )


def main() -> None:
    """FontRobotMotionBuilder の単体動作を確認する。"""
    from pathlib import Path

    from font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader

    kanjivg_directory = Path(__file__).resolve().parent / "data" / "kanjiVG"

    loader = FontKanjiVGStrokeLoader(
        kanjivg_directory=kanjivg_directory,
        height=40.0,
        spacing=5.0,
        curve_division=20,
    )

    stroke_glyph = loader.load_text(
        text="島",
    )

    builder = FontRobotMotionBuilder(
        pen_lift_height=5.0,
        drawing_speed=10.0,
        travel_speed=30.0,
    )

    commands = builder.build(
        stroke_glyph=stroke_glyph,
    )

    for command in commands:
        print(command)


if __name__ == "__main__":
    main()
