#!/usr/bin/env python3
"""COBOTTA 文字書字 ese774_frame サーバー起動例。"""

from pathlib import Path
import logging

from glyph_motion.font_bcap_cobotta_writer import FontBcapCobottaWriterConfig
from glyph_motion.server_fastapi.server import run


# SERVER_HOST = "0.0.0.0"
SERVER_HOST = "10.170.10.38"
SERVER_PORT = 8000
LOG_LEVEL = "INFO"

WRITER_CONFIG = FontBcapCobottaWriterConfig(
    # host="10.170.10.53", # cobotta3
    host="10.170.10.36",  # cobotta2
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
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
    )
    run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        writer_config=WRITER_CONFIG,
        log_level=LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
