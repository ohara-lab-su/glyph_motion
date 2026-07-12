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
    # KanjiVGデータを格納したディレクトリ。Noneの場合はサーバー側の既定値を使用する。
    kanjivg_directory=Path(
        # r"C:\Users\nakada\zaiene_dev\glyph_motion\data\kanjiVG"
        # r"C:\Users\nakada\Desktop\kanji",
        r"C:\opt\ese774\bin\glyph_motion\kanji",
    ),
    host="10.170.10.36",  # cobotta2
    # host="10.170.10.53",  # cobotta3
    port=5007,
    # 1行分の書字領域の幅（mm）。
    workspace_width=200.0,
    # 1行分の書字領域の高さ（mm）。
    workspace_height=200.0,
    # 1文字に割り当てるセルの幅（mm）。
    cell_width=8.0,
    # 1文字に割り当てるセルの高さ（mm）。
    cell_height=8.0,
    # セル内に描画する文字の高さ（mm）。
    character_height=7.0,
    # 曲線を直線分割するときの分割数。
    curve_division=16,
    # 筆画間でペンを持ち上げる高さ（mm）。
    # pen_lift_mm=1.7,
    pen_lift_mm=17,
    # 文字座標Xをロボット座標へ変換するときの符号。
    robot_x_sign=1.0,
    # 文字座標Yをロボット座標へ変換するときの符号。
    robot_y_sign=1.0,
    # 文字座標のX軸とY軸をロボット座標へ割り当てる際に入れ替えるかどうか。
    robot_swap_xy=True,
    # 横書き時の文字進行方向。縦書き時には使用しない。
    line_direction="left_to_right",
    # line_direction="right_to_left",
    # 文字列を横書きまたは縦書きのどちらで配置するか。
    writing_direction="horizontal",
    # writing_direction="vertical",
    # 縦書き時の文字進行方向。横書き時には使用しない。
    vertical_direction="top_to_bottom",
    # vertical_direction="bottom_to_top",
    # 各文字をセル内で左右反転するかどうか。
    # mirror_horizontal=False,
    mirror_horizontal=True,
    # 各文字をセル内で上下反転するかどうか。
    mirror_vertical=False,
    # 筆画を描画するときのロボット速度。
    drawing_speed=35,
    # ペンを上げた状態で移動するときのロボット速度。
    travel_speed=40,
    # ペンを上下させるときのロボット速度。
    pen_speed=20,
    # ロボット動作の加速度設定。
    accel=100,
    # ロボット動作の減速度設定。
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
