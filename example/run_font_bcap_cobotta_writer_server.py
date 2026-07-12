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
    kanjivg_directory=Path(
        # r"C:\Users\nakada\zaiene_dev\glyph_motion\data\kanjiVG"
        r"C:\Users\nakada\Desktop\kanji",
    ),
    host="10.170.10.36",  # cobotta2
    # host="10.170.10.53",  # cobotta3
    port=5007,
    # 書字ワークスペースの大きさ
    workspace_width=200.0,
    workspace_height=200.0,
    # 一文字の箱の大きさ
    cell_width=8.0,
    cell_height=8.0,
    # 箱の中の文字の高さ
    character_height=7.0,
    # ---- ベジェ曲線の分割数
    curve_division=16,
    # ペン上げ高さ [mm]
    pen_lift_mm=1.0,
    # ロボット座標系の方向
    robot_x_sign=1.0,
    robot_y_sign=1.0,
    # ロボット座標系をxy入れ替え
    robot_swap_xy=True,
    # 横書き時の進行方向
    line_direction="left_to_right",
    # 横書き・縦書き
    writing_direction="horizontal",
    # 縦書き時の進行方向
    vertical_direction="top_to_bottom",
    # 文字の左右反転
    mirror_horizontal=False,
    # 文字の上下反転
    mirror_vertical=False,
    # 書字速度
    drawing_speed=35,
    # 空走速度
    travel_speed=40,
    # ペン上下速度
    pen_speed=20,
    accel=100,
    decel=100,
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
