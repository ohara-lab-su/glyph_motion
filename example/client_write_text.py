#!/usr/bin/env python3
"""COBOTTA 文字書字 ese774_frame 同期クライアント例。"""

from glyph_motion.server_fastapi.clients import SyncCobottaWriterClient


SERVER_IP = "10.170.10.38"
SERVER_PORT = 8000
TEXT = "島根"


def main() -> None:
    client = SyncCobottaWriterClient(
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
        timeout_sec=180.0,
    )

    client.set_params(
        kanjivg_directory=None,
        workspace_width=200.0,
        workspace_height=10.0,
        cell_width=8.0,
        cell_height=8.0,
        character_height=7.0,
        curve_division=16,
        pen_lift_mm=1.0,
        robot_x_sign=1.0,
        robot_y_sign=1.0,
        robot_swap_xy=True,
        line_direction="left_to_right",
        writing_direction="horizontal",
        mirror_horizontal=False,
        mirror_vertical=False,
        drawing_speed=35,
        travel_speed=40,
        pen_speed=20,
        accel=100,
        decel=100,
    )

    result = client.write(
        text=TEXT,
        start_height_mm=1.0,
        return_to_start=True,
    )
    print(result)


if __name__ == "__main__":
    main()
