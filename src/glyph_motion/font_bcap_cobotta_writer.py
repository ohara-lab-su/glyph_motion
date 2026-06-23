#!/usr/bin/env python3
"""
K.NAKADA, kengo.nakada@gmail.com

COBOTTA b-CAP を用いて筆順付き文字を書く制御クラスを定義する。

本モジュールは run スクリプトではなく、サーバーやクライアントから利用する
クラスライブラリである。フォント処理は FontRobotWriter に委譲し、COBOTTA 固有の
接続、原点設定、速度設定、相対移動実行だけを担当する。
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union
import logging
import math
import time

from cobotta2.cobotta_bcap import CobottaBcap
from glyph_motion.font_robot_motion_builder import FontRobotMotionCommand
from glyph_motion.font_robot_writer import FontRobotWriter


@dataclass
class CobottaBcapFontWriterConfig:
    """COBOTTA b-CAP 文字書字制御の設定である。

    サーバー API 化する場合、この dataclass の各フィールドを API から更新する。
    CLI 引数やモジュール内固定値には依存しない。
    """

    host: str = "10.170.10.53"
    port: int = 5007
    kanjivg_directory: Path = Path(".") / "data" / "kanjiVG"

    layout: str = "horizontal"
    character_height_mm: float = 40.0
    character_spacing_mm: float = 5.0
    pen_lift_height_mm: float = 5.0
    curve_division: int = 20

    drawing_speed: int = 20
    travel_speed: int = 60
    pen_up_speed: int = 40
    pen_down_speed: int = 20
    approach_speed: int = 30
    accel: float = 60.0
    decel: float = 60.0

    move_interval_sec: float = 0.0
    max_travel_step_mm: float = 10.0
    skip_zero_move: bool = True
    zero_move_epsilon: float = 1.0e-6

    origin_mode: str = "current_as_first_stroke"
    surface_z_mode: str = "current"
    robot_origin_x: float = 250.0
    robot_origin_y: float = 0.0
    robot_surface_z: float = 120.0
    approach_lift_height_mm: float = 10.0

    robot_x_sign: float = 1.0
    robot_y_sign: float = 1.0
    robot_z_sign: float = 1.0
    robot_x_scale: float = 1.0
    robot_y_scale: float = 1.0
    robot_z_scale: float = 1.0
    robot_drx: float = 0.0
    robot_dry: float = 0.0
    robot_drz: float = 0.0

    reset_error_on_start: bool = True
    motor_on_on_start: bool = True
    motor_off_on_finish: bool = False
    give_arm_on_finish: bool = True


class CobottaBcapFontWriter:
    """COBOTTA b-CAP を用いて任意文字列を書く制御クラスである。"""

    def __init__(
        self,
        config: CobottaBcapFontWriterConfig,
        bcap: Optional[CobottaBcap] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.config = config
        self._bcap = bcap
        self._owns_bcap = bcap is None
        self._prepared = False
        self._last_speed: Optional[int] = None
        self._logger = logger or logging.getLogger(__name__)

    @property
    def bcap(self) -> Optional[CobottaBcap]:
        """現在利用している CobottaBcap インスタンスを返す。"""
        return self._bcap

    def update_config(self, **kwargs: object) -> None:
        """設定値をまとめて更新する。

        Args:
            **kwargs: CobottaBcapFontWriterConfig のフィールド名と値である。
        """
        for key, value in kwargs.items():
            if not hasattr(self.config, key):
                raise KeyError("unknown config key: {}".format(key))
            setattr(self.config, key, value)

    def set_text_parameters(
        self,
        *,
        character_height_mm: Optional[float] = None,
        character_spacing_mm: Optional[float] = None,
        pen_lift_height_mm: Optional[float] = None,
        curve_division: Optional[int] = None,
        layout: Optional[str] = None,
    ) -> None:
        """文字生成条件を更新する。"""
        if character_height_mm is not None:
            self.config.character_height_mm = float(character_height_mm)
        if character_spacing_mm is not None:
            self.config.character_spacing_mm = float(character_spacing_mm)
        if pen_lift_height_mm is not None:
            self.config.pen_lift_height_mm = float(pen_lift_height_mm)
        if curve_division is not None:
            self.config.curve_division = int(curve_division)
        if layout is not None:
            self.config.layout = str(layout)

    def set_motion_parameters(
        self,
        *,
        drawing_speed: Optional[int] = None,
        travel_speed: Optional[int] = None,
        pen_up_speed: Optional[int] = None,
        pen_down_speed: Optional[int] = None,
        approach_speed: Optional[int] = None,
        accel: Optional[float] = None,
        decel: Optional[float] = None,
        move_interval_sec: Optional[float] = None,
        max_travel_step_mm: Optional[float] = None,
        curve_division: Optional[int] = None,
    ) -> None:
        """ロボット移動速度、加減速、投入間隔、分割密度を更新する。"""
        if drawing_speed is not None:
            self.config.drawing_speed = int(drawing_speed)
        if travel_speed is not None:
            self.config.travel_speed = int(travel_speed)
        if pen_up_speed is not None:
            self.config.pen_up_speed = int(pen_up_speed)
        if pen_down_speed is not None:
            self.config.pen_down_speed = int(pen_down_speed)
        if approach_speed is not None:
            self.config.approach_speed = int(approach_speed)
        if accel is not None:
            self.config.accel = float(accel)
        if decel is not None:
            self.config.decel = float(decel)
        if move_interval_sec is not None:
            self.config.move_interval_sec = float(move_interval_sec)
        if max_travel_step_mm is not None:
            self.config.max_travel_step_mm = float(max_travel_step_mm)
        if curve_division is not None:
            self.config.curve_division = int(curve_division)

        if self._prepared and self._bcap is not None:
            self._apply_accel_decel()

    def set_origin_parameters(
        self,
        *,
        origin_mode: Optional[str] = None,
        surface_z_mode: Optional[str] = None,
        robot_origin_x: Optional[float] = None,
        robot_origin_y: Optional[float] = None,
        robot_surface_z: Optional[float] = None,
        approach_lift_height_mm: Optional[float] = None,
    ) -> None:
        """書字原点と書字面 Z の定義を更新する。"""
        if origin_mode is not None:
            self.config.origin_mode = str(origin_mode)
        if surface_z_mode is not None:
            self.config.surface_z_mode = str(surface_z_mode)
        if robot_origin_x is not None:
            self.config.robot_origin_x = float(robot_origin_x)
        if robot_origin_y is not None:
            self.config.robot_origin_y = float(robot_origin_y)
        if robot_surface_z is not None:
            self.config.robot_surface_z = float(robot_surface_z)
        if approach_lift_height_mm is not None:
            self.config.approach_lift_height_mm = float(approach_lift_height_mm)

    def connect(self) -> None:
        """COBOTTA b-CAP へ接続する。"""
        if self._bcap is None:
            self._bcap = CobottaBcap(
                host=self.config.host,
                port=self.config.port,
            )
            self._owns_bcap = True

        if self._bcap.connect() is False:
            raise RuntimeError("CobottaBcap.connect() failed")

    def prepare(self) -> None:
        """TakeArm、MotorOn、加減速設定、開始姿勢準備を行う。"""
        bcap = self._require_bcap()

        if self.config.reset_error_on_start:
            self._reset_error_if_needed()

        if bcap.take_arm() is False:
            raise RuntimeError("CobottaBcap.take_arm() failed")

        if self.config.motor_on_on_start:
            if bcap.motor_on() is False:
                raise RuntimeError("CobottaBcap.motor_on() failed")

        self._apply_accel_decel()
        self.prepare_start_pose()
        self._prepared = True

    def close(self) -> None:
        """終了処理を行う。"""
        bcap = self._bcap
        if bcap is None:
            return

        try:
            if self.config.motor_off_on_finish:
                bcap.motor_off()
        finally:
            try:
                if self.config.give_arm_on_finish:
                    bcap.give_arm()
            finally:
                if self._owns_bcap:
                    bcap.disconnect()
                self._bcap = None
                self._prepared = False

    def halt(self) -> None:
        """ロボット動作を停止する。"""
        bcap = self._require_bcap()
        bcap.halt()

    def get_current_position(self) -> List[float]:
        """COBOTTA の現在 P 座標を取得する。"""
        bcap = self._require_bcap()
        if hasattr(bcap, "get_current_position"):
            position = bcap.get_current_position()
        else:
            position = bcap.get_curpos()

        if position is False or position is None:
            raise RuntimeError("CobottaBcap.get_current_position() failed")

        values = list(position)
        if len(values) < 6:
            raise RuntimeError("current position length is invalid: {}".format(values))
        return [float(v) for v in values[:6]]

    def build_commands(
        self,
        text: str,
        layout: Optional[str] = None,
    ) -> List[FontRobotMotionCommand]:
        """文字列から COBOTTA 実行前の抽象ロボット命令列を作る。"""
        writer = FontRobotWriter(
            kanjivg_directory=Path(self.config.kanjivg_directory),
            height=float(self.config.character_height_mm),
            character_spacing=float(self.config.character_spacing_mm),
            pen_lift_height=float(self.config.pen_lift_height_mm),
            curve_division=int(self.config.curve_division),
            drawing_speed=float(self.config.drawing_speed),
            travel_speed=float(self.config.travel_speed),
        )
        commands = writer.write(
            text=text,
            layout=layout or self.config.layout,
        )
        return self.normalize_commands_for_origin_mode(commands)

    def write_text(
        self,
        text: str,
        layout: Optional[str] = None,
        *,
        execute: bool = True,
    ) -> Dict[str, object]:
        """任意文字列を書く API である。

        Args:
            text: 書く文字列である。
            layout: 横書き/縦書きである。None の場合は設定値を使う。
            execute: False の場合はロボットへ投入せず、命令数だけ返す。

        Returns:
            実行結果を表す dict である。
        """
        commands = self.build_commands(
            text=text,
            layout=layout,
        )
        if execute:
            if self._bcap is None:
                self.connect()
            if not self._prepared:
                self.prepare()
            self.execute_commands(commands)

        return {
            "text": text,
            "layout": layout or self.config.layout,
            "command_count": len(commands),
            "execute": execute,
            "config": self.to_dict(),
        }

    def execute_commands(self, commands: Iterable[FontRobotMotionCommand]) -> None:
        """FontRobotMotionCommand 列を COBOTTA b-CAP の相対移動へ変換して実行する。"""
        bcap = self._require_bcap()
        for index, command in enumerate(commands):
            dpose = self.to_bcap_dpose(command)
            speed = self.resolve_speed(command)

            for split_index, split_dpose in enumerate(
                self.split_dpose_if_needed(dpose, command.pen_down)
            ):
                if self._is_zero_move(split_dpose) and self.config.skip_zero_move:
                    continue

                self._logger.info(
                    "command=%d split=%d stroke=%d point=%d pen_down=%s speed=%s dpose=%s",
                    index,
                    split_index,
                    command.stroke_index,
                    command.point_index,
                    command.pen_down,
                    speed,
                    split_dpose,
                )

                self._set_speed_if_needed(speed)
                ok = bcap.robo_dmove(split_dpose, coord_mode="P")
                if ok is False:
                    raise RuntimeError("CobottaBcap.robo_dmove() failed")

                if self.config.move_interval_sec > 0.0:
                    time.sleep(self.config.move_interval_sec)

    def prepare_start_pose(self) -> None:
        """原点モードと書字面 Z モードに従って開始姿勢を整える。"""
        current = self.get_current_position()
        surface_z = current[2]

        if self.config.surface_z_mode == "absolute":
            surface_z = float(self.config.robot_surface_z)
        elif self.config.surface_z_mode != "current":
            raise ValueError(
                "unknown surface_z_mode: {}".format(self.config.surface_z_mode)
            )

        self._logger.info("current P: %s", current)
        self._logger.info("surface_z: %s", surface_z)
        self._logger.info("origin_mode: %s", self.config.origin_mode)

        if self.config.origin_mode in ("current_as_origin", "current_as_first_stroke"):
            if self.config.surface_z_mode == "absolute":
                dz = surface_z - current[2]
                if abs(dz) > self.config.zero_move_epsilon:
                    self.safe_move(
                        [0.0, 0.0, dz, 0.0, 0.0, 0.0], self.config.approach_speed
                    )
            return

        if self.config.origin_mode != "absolute_origin":
            raise ValueError("unknown origin_mode: {}".format(self.config.origin_mode))

        safe_z = (
            surface_z
            + float(self.config.approach_lift_height_mm) * self.config.robot_z_sign
        )
        self.safe_move(
            [0.0, 0.0, safe_z - current[2], 0.0, 0.0, 0.0], self.config.approach_speed
        )

        current_after_z = self.get_current_position()
        dx = float(self.config.robot_origin_x) - current_after_z[0]
        dy = float(self.config.robot_origin_y) - current_after_z[1]
        self.safe_move([dx, dy, 0.0, 0.0, 0.0, 0.0], self.config.approach_speed)

        current_after_xy = self.get_current_position()
        self.safe_move(
            [0.0, 0.0, surface_z - current_after_xy[2], 0.0, 0.0, 0.0],
            self.config.approach_speed,
        )

    def safe_move(self, dpose: Sequence[float], speed: int) -> None:
        """速度設定後、必要なら分割して相対移動する。"""
        bcap = self._require_bcap()
        self._set_speed_if_needed(int(speed))
        for split_dpose in self.split_dpose_if_needed(dpose, pen_down=False):
            if self._is_zero_move(split_dpose) and self.config.skip_zero_move:
                continue
            self._logger.info("prepare dpose=%s", split_dpose)
            ok = bcap.robo_dmove(split_dpose, coord_mode="P")
            if ok is False:
                raise RuntimeError("CobottaBcap.robo_dmove() failed in safe_move")
            if self.config.move_interval_sec > 0.0:
                time.sleep(self.config.move_interval_sec)

    def normalize_commands_for_origin_mode(
        self,
        commands: List[FontRobotMotionCommand],
    ) -> List[FontRobotMotionCommand]:
        """origin_mode に従って初期 XY 移動を補正する。"""
        mode = self.config.origin_mode
        if mode in ("current_as_origin", "absolute_origin"):
            return commands

        if mode != "current_as_first_stroke":
            raise ValueError("unknown origin_mode: {}".format(mode))

        normalized: List[FontRobotMotionCommand] = []
        first_xy_travel_done = False

        for command in commands:
            if (
                not first_xy_travel_done
                and not command.pen_down
                and (abs(command.dx) > 0.0 or abs(command.dy) > 0.0)
            ):
                normalized.append(
                    replace(
                        command,
                        dx=0.0,
                        dy=0.0,
                    )
                )
                first_xy_travel_done = True
            else:
                normalized.append(command)

        return normalized

    def to_bcap_dpose(self, command: FontRobotMotionCommand) -> List[float]:
        """FontRobotMotionCommand を [dx, dy, dz, drx, dry, drz] へ変換する。"""
        return [
            float(command.dx) * self.config.robot_x_scale * self.config.robot_x_sign,
            float(command.dy) * self.config.robot_y_scale * self.config.robot_y_sign,
            float(command.dz) * self.config.robot_z_scale * self.config.robot_z_sign,
            float(self.config.robot_drx),
            float(self.config.robot_dry),
            float(self.config.robot_drz),
        ]

    def resolve_speed(self, command: FontRobotMotionCommand) -> int:
        """命令種別から実行速度を決める。"""
        if command.pen_down:
            if (
                abs(command.dz) > 0.0
                and abs(command.dx) == 0.0
                and abs(command.dy) == 0.0
            ):
                return int(self.config.pen_down_speed)
            return int(
                command.speed
                if command.speed is not None
                else self.config.drawing_speed
            )

        if abs(command.dz) > 0.0 and abs(command.dx) == 0.0 and abs(command.dy) == 0.0:
            return int(self.config.pen_up_speed)
        return int(
            command.speed if command.speed is not None else self.config.travel_speed
        )

    def split_dpose_if_needed(
        self, dpose: Sequence[float], pen_down: bool
    ) -> List[List[float]]:
        """非筆記 XY 移動を max_travel_step_mm 以下へ分割する。"""
        dx = float(dpose[0])
        dy = float(dpose[1])
        dz = float(dpose[2])

        if pen_down:
            return [list(dpose)]

        max_step = float(self.config.max_travel_step_mm)
        distance_xy = math.hypot(dx, dy)
        if distance_xy <= max_step or max_step <= 0.0:
            return [list(dpose)]

        count = int(math.ceil(distance_xy / max_step))
        return [
            [
                dx / count,
                dy / count,
                dz / count,
                float(dpose[3]) / count,
                float(dpose[4]) / count,
                float(dpose[5]) / count,
            ]
            for _ in range(count)
        ]

    def to_dict(self) -> Dict[str, object]:
        """現在設定を dict として返す。"""
        values = dict(self.config.__dict__)
        values["kanjivg_directory"] = str(values["kanjivg_directory"])
        return values

    def _apply_accel_decel(self) -> None:
        bcap = self._require_bcap()
        if bcap.set_accel(float(self.config.accel)) is False:
            raise RuntimeError("CobottaBcap.set_accel() failed")
        if bcap.set_decel(float(self.config.decel)) is False:
            raise RuntimeError("CobottaBcap.set_decel() failed")

    def _reset_error_if_needed(self) -> None:
        bcap = self._require_bcap()
        try:
            err_count = bcap.get_error_count()
            if int(err_count) > 0:
                bcap.reset_error()
        except Exception:
            bcap.reset_error()

    def _set_speed_if_needed(self, speed: int) -> None:
        bcap = self._require_bcap()
        if self._last_speed == speed:
            return
        if bcap.set_speed(int(speed)) is False:
            raise RuntimeError("CobottaBcap.set_speed() failed")
        self._last_speed = int(speed)

    def _require_bcap(self) -> CobottaBcap:
        if self._bcap is None:
            raise RuntimeError("CobottaBcap is not connected")
        return self._bcap

    def _is_zero_move(self, dpose: Sequence[float]) -> bool:
        eps = float(self.config.zero_move_epsilon)
        return all(abs(float(v)) <= eps for v in dpose[:6])


__all__ = [
    "CobottaBcapFontWriter",
    "CobottaBcapFontWriterConfig",
]
