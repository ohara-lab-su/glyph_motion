#!/usr/bin/env python3
"""COBOTTA 文字書字 ese774_frame 同期クライアント例。"""

from glyph_motion.server_fastapi.clients import SyncCobottaWriterClient


SERVER_IP = "10.170.10.38"  # server2
# SERVER_IP = "10.170.10.41" # server3
SERVER_PORT = 8000
TEXT = "島根大学"
# TEXT = "島根大学材料エネルギー学部"


def main() -> None:
    client = SyncCobottaWriterClient(
        # 接続先サーバーのIPアドレス。
        server_ip=SERVER_IP,
        # 接続先サーバーのポート番号。
        server_port=SERVER_PORT,
    )

    client.connect()
    client.reset_error()
    client.take_arm()
    client.motor_on()

    client.set_params(
        # KanjiVGデータを格納したディレクトリ。Noneの場合はサーバー側の既定値を使用する。
        kanjivg_directory=None,
        # 1行分の書字領域の幅（mm）。
        workspace_width=265.0,
        # 1行分の書字領域の高さ（mm）。
        workspace_height=12.0,
        # 1文字に割り当てるセルの幅（mm）。
        cell_width=10.0,
        # 1文字に割り当てるセルの高さ（mm）。
        cell_height=10.0,
        # セル内に描画する文字の高さ（mm）。
        character_height=8.8,
        # 曲線を直線分割するときの分割数。
        curve_division=16,
        # 筆画間でペンを持ち上げる高さ（mm）。
        pen_lift_mm=2.0,
        # pen_lift_mm=17,
        # 文字座標Xをロボット座標へ変換するときの符号。
        robot_x_sign=1.0,
        # 文字座標Yをロボット座標へ変換するときの符号。
        robot_y_sign=1.0,
        # 文字座標のX軸とY軸をロボット座標へ割り当てる際に入れ替えるかどうか。
        robot_swap_xy=True,
        # 横書き時の文字進行方向。縦書き時には使用しない。
        # line_direction="left_to_right",
        line_direction="right_to_left",
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
        # mirror_vertical=True,  # bug
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

    result = client.write(
        # 書字する文字列。
        text=TEXT,
        # 書字開始位置から書字面までペンを下げる距離（mm）。
        start_height_mm=2.4,
        # 書字完了後に開始位置へ戻るかどうか。
        return_to_start=True,
    )
    print(result)

    client.give_arm()
    client.disconnect()


if __name__ == "__main__":
    main()
