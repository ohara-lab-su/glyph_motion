#!/usr/bin/env python3
"""
COBOTTA b-CAP 文字書字クラスの最小利用例である。

本ファイルは設定例と手動実行用のクライアントである。実際の制御ロジックは
font_bcap_cobotta_writer.CobottaBcapFontWriter に置く。
"""

from pathlib import Path
import logging

from glyph_motion.font_bcap_cobotta_writer import CobottaBcapFontWriter
from glyph_motion.font_bcap_cobotta_writer import CobottaBcapFontWriterConfig


EXECUTE_ROBOT = True
# TEXT = "島根"
TEXT = "中田"

CONFIG = CobottaBcapFontWriterConfig(
    host="10.170.10.53",
    port=5007,
    kanjivg_directory=Path(r"C:\Users\nakada\Desktop\kanji"),
    layout="horizontal",
    character_height_mm=40.0,
    character_spacing_mm=5.0,
    pen_lift_height_mm=5.0,
    curve_division=12,
    drawing_speed=35,
    travel_speed=80,
    pen_up_speed=60,
    pen_down_speed=25,
    approach_speed=40,
    accel=80.0,
    decel=80.0,
    move_interval_sec=0.0,
    max_travel_step_mm=15.0,
    origin_mode="current_as_first_stroke",
    surface_z_mode="current",
)


def main() -> None:
    """文字書字クラスを使って文字を書く。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
    )

    writer = CobottaBcapFontWriter(config=CONFIG)
    try:

        result = writer.write_text(
            text=TEXT,
            execute=EXECUTE_ROBOT,
        )
        logging.info("result: %s", result)

    except Exception:
        logging.exception("font b-CAP writing failed")
        try:
            if writer.bcap is not None:
                writer.halt()
                writer.bcap.reset_error()
        except Exception:
            pass
        raise
    finally:
        writer.close()


if __name__ == "__main__":
    main()
