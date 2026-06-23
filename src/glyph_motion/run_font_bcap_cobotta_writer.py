#!/usr/bin/env python3
"""
KanjiVG の筆順付き stroke を COBOTTA b-CAP の相対移動で実行する。

本ファイルは、joypad 系と同じ高速経路である CobottaBcap.robo_dmove() を直接使う。
ORiN2/COM 側の CobottaCtrl は使わない。
CLI 引数は使わず、設定は本ファイル先頭の定数だけで行う。
"""

from pathlib import Path
from typing import Iterable, List, Optional
import logging
import time

from cobotta2.cobotta_bcap import CobottaBcap
from glyph_motion.font_robot_writer import FontRobotWriter
from glyph_motion.font_robot_motion_builder import FontRobotMotionCommand


# ============================================================
# 実行設定
# ============================================================

# 実機を動かす場合は True にする。
# False の場合も、b-CAP へ接続せず、生成された dpose を表示する。
EXECUTE_ROBOT = False

# COBOTTA b-CAP 接続先。
COBOTTA_HOST = "10.170.10.37"
COBOTTA_PORT = 5007

# KanjiVG の SVG ディレクトリ。
# None の場合は下の KANJIVG_DIRECTORY_CANDIDATES から実在するものを自動選択する。
# Windows では Path.home() / "Desktop" / "data" / "kanjiVG" が通常候補になる。
KANJIVG_DIRECTORY = None

KANJIVG_DIRECTORY_CANDIDATES = [
    Path.home() / "Desktop" / "data" / "kanjiVG",
    Path.home() / "Desktop" / "data" / "kanjivg",
    Path.home() / "data" / "kanjiVG",
    Path.home() / "data" / "kanjivg",
    Path.cwd() / "data" / "kanjiVG",
    Path.cwd() / "data" / "kanjivg",
]

# 書く文字列と配置。
TEXT = "島根"
LAYOUT = "horizontal"  # "horizontal" or "vertical"

# 文字サイズ。単位はロボット座標へ渡す mm 相当として扱う。
CHARACTER_HEIGHT_MM = 40.0
CHARACTER_SPACING_MM = 5.0
PEN_LIFT_HEIGHT_MM = 5.0
CURVE_DIVISION = 20

# COBOTTA 速度設定。CobottaBcap.set_speed() に渡す値である。
DRAWING_SPEED = 10
TRAVEL_SPEED = 30
ACCEL = 30.0
DECEL = 30.0

# glyph_motion の XY を COBOTTA の P 座標差分へ写像する符号。
# 置いた紙・ペン姿勢に合わせてここだけ変更する。
ROBOT_X_SIGN = 1.0
ROBOT_Y_SIGN = 1.0
ROBOT_Z_SIGN = 1.0

# 文字座標の倍率。通常は 1.0。
ROBOT_X_SCALE = 1.0
ROBOT_Y_SCALE = 1.0
ROBOT_Z_SCALE = 1.0

# 姿勢は固定する。相対姿勢移動は行わない。
ROBOT_DRX = 0.0
ROBOT_DRY = 0.0
ROBOT_DRZ = 0.0

# NEXT 投入を詰めすぎないための最小待ち時間。
MOVE_INTERVAL_SEC = 0.02

# 起動・終了時の扱い。
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

            logging.info(
                "command=%d stroke=%d point=%d pen_down=%s speed=%s dpose=%s",
                index,
                command.stroke_index,
                command.point_index,
                command.pen_down,
                speed,
                dpose,
            )

            if self._bcap is None:
                continue

            self._set_speed_if_needed(speed)
            ok = self._bcap.robo_dmove(dpose, coord_mode="P")
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


def resolve_kanjivg_directory() -> Path:
    """KanjiVG SVG ディレクトリを設定定数から解決する。

    CLI 引数は使わない。
    KANJIVG_DIRECTORY が指定されていればそれを使う。
    None の場合は KANJIVG_DIRECTORY_CANDIDATES を順に調べる。
    """
    if KANJIVG_DIRECTORY is not None:
        directory = Path(KANJIVG_DIRECTORY).expanduser()
        if directory.exists() is False:
            raise FileNotFoundError("KANJIVG_DIRECTORY が存在しない: {}".format(directory))
        return directory

    checked = []
    for candidate in KANJIVG_DIRECTORY_CANDIDATES:
        directory = Path(candidate).expanduser()
        checked.append(str(directory))
        if directory.exists():
            return directory

    raise FileNotFoundError(
        "KanjiVG SVG ディレクトリが見つからない。"
        "KANJIVG_DIRECTORY に明示設定するか、"
        "KANJIVG_DIRECTORY_CANDIDATES を修正すること。checked={}".format(checked)
    )


def build_commands() -> List[FontRobotMotionCommand]:
    """KanjiVG からロボット筆記用相対移動命令列を作る。"""
    kanjivg_directory = resolve_kanjivg_directory()
    logging.info("KanjiVG directory: %s", kanjivg_directory)

    writer = FontRobotWriter(
        kanjivg_directory=kanjivg_directory,
        height=CHARACTER_HEIGHT_MM,
        character_spacing=CHARACTER_SPACING_MM,
        pen_lift_height=PEN_LIFT_HEIGHT_MM,
        curve_division=CURVE_DIVISION,
        drawing_speed=float(DRAWING_SPEED),
        travel_speed=float(TRAVEL_SPEED),
    )
    return writer.write(
        text=TEXT,
        layout=LAYOUT,
    )


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
        format="%(asctime)s %(levelname)s %(message)s",
    )

    commands = build_commands()
    logging.info("generated commands: %d", len(commands))

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
