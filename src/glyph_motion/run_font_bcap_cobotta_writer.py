#!/usr/bin/env python3
"""
KanjiVG の筆順付き stroke を COBOTTA b-CAP の相対移動で実行する。

joypad 系と同じ高速経路である CobottaBcap.robo_dmove() を直接使う。
CLI 引数は使わず、設定は本ファイル先頭の定数だけで行う。

重要:
    文字の論理座標とロボット実座標は別である。
    本ファイルでは ORIGIN_MODE と SURFACE_Z_MODE により、
    どの実機位置を文字座標の基準にするかを明示する。
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
import logging
import math
import time

from cobotta2.cobotta_bcap import CobottaBcap
from glyph_motion.font_robot_writer import FontRobotWriter
from glyph_motion.font_robot_motion_builder import FontRobotMotionCommand


# ============================================================
# 実行設定
# ============================================================

EXECUTE_ROBOT = True

COBOTTA_HOST = "10.170.10.53"
COBOTTA_PORT = 5007

KANJIVG_DIRECTORY = Path(r"C:\Users\nakada\Desktop\kanji")

TEXT = "島根"
LAYOUT = "horizontal"  # "horizontal" or "vertical"

# 一文字の高さ。単位は mm としてロボット座標に渡す。
CHARACTER_HEIGHT_MM = 40.0
CHARACTER_SPACING_MM = 5.0
PEN_LIFT_HEIGHT_MM = 5.0
CURVE_DIVISION = 20

DRAWING_SPEED = 10
TRAVEL_SPEED = 30
ACCEL = 30.0
DECEL = 30.0

# ============================================================
# 原点・紙面設定
# ============================================================

# 文字座標の原点をどこに置くかを指定する。
#
# "current_as_origin":
#     実行開始時の現在位置 XY を、文字座標の (0, 0) とする。
#     最初の筆画始点まで XY 移動する。
#
# "current_as_first_stroke":
#     実行開始時の現在位置 XY を、最初の筆画始点とする。
#     最初の大きな XY 移動を消す。試運転ではこのモードが安全である。
#
# "absolute_origin":
#     ROBOT_ORIGIN_X/Y を、文字座標の (0, 0) とする。
#     実行開始時に現在位置を読み、そこから指定原点へ移動する。
ORIGIN_MODE = "current_as_first_stroke"

# ORIGIN_MODE = "absolute_origin" の場合だけ使う。
ROBOT_ORIGIN_X = 250.0
ROBOT_ORIGIN_Y = 0.0

# Z 書字面の決め方。
#
# "current":
#     実行開始時の現在 Z を書字面とする。
#
# "absolute":
#     ROBOT_SURFACE_Z を書字面とする。
SURFACE_Z_MODE = "current"
ROBOT_SURFACE_Z = 120.0

# 絶対原点へ移動するときの退避高さ。
APPROACH_LIFT_HEIGHT_MM = 10.0

# 初回 XY 移動や筆画間移動を分割する最大移動量。
# 可動範囲外そのものは解決しないが、NEXT 投入の粗すぎる移動を避ける。
MAX_TRAVEL_STEP_MM = 5.0

# XY と Z の向き・倍率。
ROBOT_X_SIGN = 1.0
ROBOT_Y_SIGN = 1.0
ROBOT_Z_SIGN = 1.0
ROBOT_X_SCALE = 1.0
ROBOT_Y_SCALE = 1.0
ROBOT_Z_SCALE = 1.0

ROBOT_DRX = 0.0
ROBOT_DRY = 0.0
ROBOT_DRZ = 0.0

MOVE_INTERVAL_SEC = 0.02

RESET_ERROR_ON_START = True
MOTOR_ON_ON_START = True
MOTOR_OFF_ON_FINISH = False
GIVE_ARM_ON_FINISH = True


class BcapFontCobottaWriter:
    """FontRobotMotionCommand を COBOTTA b-CAP 相対移動で実行する。"""

    def __init__(self, bcap: Optional[CobottaBcap]) -> None:
        self._bcap = bcap
        self._last_speed: Optional[int] = None

    def execute(self, commands: Iterable[FontRobotMotionCommand]) -> None:
        """命令列を順に COBOTTA へ投入する。"""
        for index, command in enumerate(commands):
            dpose = self._to_bcap_dpose(command)
            speed = self._resolve_speed(command)

            for split_index, split_dpose in enumerate(
                split_dpose_if_needed(dpose, command.pen_down)
            ):
                logging.info(
                    "command=%d split=%d stroke=%d point=%d pen_down=%s speed=%s dpose=%s",
                    index,
                    split_index,
                    command.stroke_index,
                    command.point_index,
                    command.pen_down,
                    speed,
                    split_dpose,
                )

                if self._bcap is None:
                    continue

                self._set_speed_if_needed(speed)
                ok = self._bcap.robo_dmove(split_dpose, coord_mode="P")
                if ok is False:
                    raise RuntimeError("CobottaBcap.robo_dmove() failed")

                if MOVE_INTERVAL_SEC > 0.0:
                    time.sleep(MOVE_INTERVAL_SEC)

    def _to_bcap_dpose(self, command: FontRobotMotionCommand) -> List[float]:
        """FontRobotMotionCommand を joypad 系と同じ [dx,dy,dz,drx,dry,drz] へ変換する。"""
        return [
            float(command.dx) * ROBOT_X_SCALE * ROBOT_X_SIGN,
            float(command.dy) * ROBOT_Y_SCALE * ROBOT_Y_SIGN,
            float(command.dz) * ROBOT_Z_SCALE * ROBOT_Z_SIGN,
            ROBOT_DRX,
            ROBOT_DRY,
            ROBOT_DRZ,
        ]

    def _resolve_speed(self, command: FontRobotMotionCommand) -> int:
        if command.speed is not None:
            return int(command.speed)
        if command.pen_down:
            return int(DRAWING_SPEED)
        return int(TRAVEL_SPEED)

    def _set_speed_if_needed(self, speed: int) -> None:
        if self._bcap is None:
            return
        if self._last_speed == speed:
            return
        ok = self._bcap.set_speed(speed)
        if ok is False:
            raise RuntimeError("CobottaBcap.set_speed() failed")
        self._last_speed = speed


def split_dpose_if_needed(dpose: Sequence[float], pen_down: bool) -> List[List[float]]:
    """非筆記 XY 移動だけを MAX_TRAVEL_STEP_MM 以下に分割する。"""
    dx = float(dpose[0])
    dy = float(dpose[1])
    dz = float(dpose[2])

    if pen_down:
        return [list(dpose)]

    distance_xy = math.hypot(dx, dy)
    if distance_xy <= MAX_TRAVEL_STEP_MM or MAX_TRAVEL_STEP_MM <= 0.0:
        return [list(dpose)]

    count = int(math.ceil(distance_xy / MAX_TRAVEL_STEP_MM))
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


def normalize_commands_for_origin_mode(
    commands: List[FontRobotMotionCommand],
) -> List[FontRobotMotionCommand]:
    """ORIGIN_MODE に従って、文字座標の初期基準を補正する。

    current_as_origin では、現在位置を文字座標 (0, 0) とするので補正しない。
    current_as_first_stroke では、最初の筆画始点を現在位置に合わせるため、
    最初の XY 移動だけを 0 にする。
    absolute_origin では、実機を指定原点へ移動した後に通常命令を実行するので補正しない。
    """
    if ORIGIN_MODE in ("current_as_origin", "absolute_origin"):
        return commands

    if ORIGIN_MODE != "current_as_first_stroke":
        raise ValueError("unknown ORIGIN_MODE: {}".format(ORIGIN_MODE))

    normalized: List[FontRobotMotionCommand] = []
    first_xy_travel_done = False

    for command in commands:
        if (
            first_xy_travel_done is False
            and command.pen_down is False
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


def build_commands() -> List[FontRobotMotionCommand]:
    """KanjiVG からロボット筆記用相対移動命令列を作る。"""
    logging.info("KanjiVG directory: %s", KANJIVG_DIRECTORY)

    writer = FontRobotWriter(
        kanjivg_directory=KANJIVG_DIRECTORY,
        height=CHARACTER_HEIGHT_MM,
        character_spacing=CHARACTER_SPACING_MM,
        pen_lift_height=PEN_LIFT_HEIGHT_MM,
        curve_division=CURVE_DIVISION,
        drawing_speed=float(DRAWING_SPEED),
        travel_speed=float(TRAVEL_SPEED),
    )

    commands = writer.write(
        text=TEXT,
        layout=LAYOUT,
    )
    return normalize_commands_for_origin_mode(commands)


def get_current_position(bcap: CobottaBcap) -> List[float]:
    """COBOTTA の現在 P 座標を取得する。"""
    position = bcap.get_curpos()
    if position is False or position is None:
        raise RuntimeError("CobottaBcap.get_curpos() failed")
    values = list(position)
    if len(values) < 6:
        raise RuntimeError("CurPos length is invalid: {}".format(values))
    return [float(v) for v in values[:6]]


def prepare_start_pose(bcap: CobottaBcap) -> None:
    """ORIGIN_MODE と SURFACE_Z_MODE に従って、実行開始位置を整える。"""
    current = get_current_position(bcap)
    surface_z = current[2]

    if SURFACE_Z_MODE == "absolute":
        surface_z = float(ROBOT_SURFACE_Z)
    elif SURFACE_Z_MODE != "current":
        raise ValueError("unknown SURFACE_Z_MODE: {}".format(SURFACE_Z_MODE))

    logging.info("current P: %s", current)
    logging.info("surface_z: %s", surface_z)
    logging.info("origin_mode: %s", ORIGIN_MODE)

    # current_as_origin / current_as_first_stroke では XY は現在位置を基準にする。
    if ORIGIN_MODE in ("current_as_origin", "current_as_first_stroke"):
        if SURFACE_Z_MODE == "absolute":
            dz = surface_z - current[2]
            if abs(dz) > 0.001:
                safe_move(bcap, [0.0, 0.0, dz, 0.0, 0.0, 0.0], TRAVEL_SPEED)
        return

    if ORIGIN_MODE != "absolute_origin":
        raise ValueError("unknown ORIGIN_MODE: {}".format(ORIGIN_MODE))

    safe_z = surface_z + float(APPROACH_LIFT_HEIGHT_MM) * ROBOT_Z_SIGN

    # 1. 現在位置から安全 Z へ移動する。
    safe_move(bcap, [0.0, 0.0, safe_z - current[2], 0.0, 0.0, 0.0], TRAVEL_SPEED)

    # 2. 安全 Z 上で指定 XY 原点へ移動する。
    current_after_z = get_current_position(bcap)
    dx = float(ROBOT_ORIGIN_X) - current_after_z[0]
    dy = float(ROBOT_ORIGIN_Y) - current_after_z[1]
    safe_move(bcap, [dx, dy, 0.0, 0.0, 0.0, 0.0], TRAVEL_SPEED)

    # 3. 書字面 Z へ降ろす。以後、生成命令の最初で PEN_LIFT_HEIGHT_MM だけ上がる。
    current_after_xy = get_current_position(bcap)
    safe_move(
        bcap, [0.0, 0.0, surface_z - current_after_xy[2], 0.0, 0.0, 0.0], TRAVEL_SPEED
    )


def safe_move(bcap: CobottaBcap, dpose: Sequence[float], speed: int) -> None:
    """速度設定後、必要なら分割して dmove する。"""
    if bcap.set_speed(int(speed)) is False:
        raise RuntimeError("CobottaBcap.set_speed() failed")

    for split_dpose in split_dpose_if_needed(dpose, pen_down=False):
        logging.info("prepare dpose=%s", split_dpose)
        ok = bcap.robo_dmove(split_dpose, coord_mode="P")
        if ok is False:
            raise RuntimeError("CobottaBcap.robo_dmove() failed in prepare_start_pose")
        if MOVE_INTERVAL_SEC > 0.0:
            time.sleep(MOVE_INTERVAL_SEC)


def prepare_bcap() -> CobottaBcap:
    """COBOTTA b-CAP を初期化し、joypad 系と同じ raw dmove 実行準備を行う。"""
    bcap = CobottaBcap(
        host=COBOTTA_HOST,
        port=COBOTTA_PORT,
    )

    if bcap.connect() is False:
        raise RuntimeError("CobottaBcap.connect() failed")

    if RESET_ERROR_ON_START:
        try:
            err_count = bcap.get_error_count()
            if int(err_count) > 0:
                bcap.reset_error()
        except Exception:
            bcap.reset_error()

    if bcap.take_arm() is False:
        raise RuntimeError("CobottaBcap.take_arm() failed")

    if MOTOR_ON_ON_START:
        if bcap.motor_on() is False:
            raise RuntimeError("CobottaBcap.motor_on() failed")

    if bcap.set_accel(ACCEL) is False:
        raise RuntimeError("CobottaBcap.set_accel() failed")
    if bcap.set_decel(DECEL) is False:
        raise RuntimeError("CobottaBcap.set_decel() failed")

    prepare_start_pose(bcap)

    return bcap


def cleanup_bcap(bcap: Optional[CobottaBcap]) -> None:
    """終了処理を行う。"""
    if bcap is None:
        return

    try:
        if MOTOR_OFF_ON_FINISH:
            bcap.motor_off()
    finally:
        try:
            if GIVE_ARM_ON_FINISH:
                bcap.give_arm()
        finally:
            bcap.disconnect()


def main() -> None:
    """筆順付き文字パスを b-CAP の robo_dmove() で実行する。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
    )

    commands = build_commands()
    logging.info("generated commands: %d", len(commands))
    logging.info("character height mm: %s", CHARACTER_HEIGHT_MM)
    logging.info("origin mode: %s", ORIGIN_MODE)
    logging.info("surface z mode: %s", SURFACE_Z_MODE)

    bcap: Optional[CobottaBcap] = None
    try:
        if EXECUTE_ROBOT:
            bcap = prepare_bcap()

        executor = BcapFontCobottaWriter(bcap=bcap)
        executor.execute(commands)

    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt: halt")
        if bcap is not None:
            bcap.halt()
        raise

    except Exception:
        logging.exception("font b-CAP writing failed")
        if bcap is not None:
            try:
                bcap.halt()
            except Exception:
                pass
            try:
                bcap.reset_error()
            except Exception:
                pass
        raise

    finally:
        cleanup_bcap(bcap)


if __name__ == "__main__":
    main()
