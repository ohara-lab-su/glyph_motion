#!/usr/bin/env python3
"""COBOTTA 文字書字 ese774_frame 同期クライアント例。"""

from glyph_motion.server_fastapi.clients import SyncCobottaWriterClient


# SERVER_IP = "127.0.0.1"
SERVER_IP = "10.170.10.38"
SERVER_PORT = 8000
TEXT = "島根"


def main() -> None:
    client = SyncCobottaWriterClient(
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
        timeout_sec=180.0,
    )
    client.set_motion_parameters(
        drawing_speed=35,
        travel_speed=80,
        pen_up_speed=60,
        pen_down_speed=25,
        accel=80.0,
        decel=80.0,
        move_interval_sec=0.0,
    )
    result = client.write_text(text=TEXT, execute=True)
    print(result)


if __name__ == "__main__":
    main()
