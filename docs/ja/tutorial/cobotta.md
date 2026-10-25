# COBOTTAで書字する

`FontBcapCobottaWriter` は、KanjiVG由来の配置済みストロークをCOBOTTAの絶対P座標へ変換し、b-CAPで書字します。

## 基本例

```python
from pathlib import Path

from glyph_motion.lib.font_bcap_cobotta_writer import (
    FontBcapCobottaWriter,
    FontBcapCobottaWriterConfig,
)

config = FontBcapCobottaWriterConfig(
    kanjivg_directory=Path("kanjivg/kanji"),
    host="10.170.10.53",
    port=5007,
    workspace_width=200.0,
    workspace_height=100.0,
    cell_width=8.0,
    cell_height=8.0,
    character_height=7.0,
    curve_division=16,
    pen_lift_mm=1.0,
    robot_x_sign=1.0,
    robot_y_sign=1.0,
    robot_swap_xy=False,
    writing_direction="horizontal",
    line_direction="left_to_right",
    drawing_speed=35,
    travel_speed=40,
    pen_speed=20,
    accel=100,
    decel=100,
)

writer = FontBcapCobottaWriter(config=config)

try:
    if not writer.connect():
        raise RuntimeError("COBOTTAへ接続できない。")
    if not writer.reset_error():
        raise RuntimeError("エラー解除に失敗した。")
    if not writer.take_arm():
        raise RuntimeError("アーム権限取得に失敗した。")
    if not writer.motor_on():
        raise RuntimeError("モータ投入に失敗した。")
    if not writer.set_accel():
        raise RuntimeError("加速度設定に失敗した。")
    if not writer.set_decel():
        raise RuntimeError("減速度設定に失敗した。")

    if not writer.write(
        text="島根大学",
        start_height_mm=1.0,
        return_to_start=True,
    ):
        raise RuntimeError("書字に失敗した。")
finally:
    writer.emergency_lift_pen()
    writer.give_arm()
    writer.disconnect()
```

## 書字面の決定

`write()` 呼び出し時の現在Z座標から `start_height_mm` を引いた位置が書字面です。

```text
surface_z = start_pose_z - start_height_mm
pen_up_z  = surface_z + pen_lift_mm
```

開始姿勢が書字面上、すなわち `start_height_mm == 0.0` の場合は、その場でペンを上げてから最初の筆画始点へ移動します。開始姿勢が既に書字面より高い場合は、その高さを維持して最初の始点へ移動します。

## 絶対座標変換

最初の `write()` の開始姿勢が文書全体の原点として保存されます。文字座標は必要に応じてXYを交換し、各軸の符号を適用した後、原点へ加算されます。姿勢成分は開始姿勢を維持します。

## 継続書字と改行

同じwriterで複数回 `write()` を呼ぶと、論理カーソルを保持して前回の続きから書けます。

```python
writer.write("島根", return_to_start=True)
writer.write("大学", return_to_start=True, new_line=False)
writer.write("材料", return_to_start=True, new_line=True)
```

`return_to_start` は物理的に呼び出し開始姿勢へ戻るかだけを制御します。次回の論理書字位置は維持されます。

横書き時の改行方向は `horizontal_new_line_direction`、縦書き時の改列方向は `vertical_new_line_direction` で指定します。未指定の場合は、反転設定から自動決定されます。

## 失敗時の退避

`emergency_lift_pen()` は、書字中に保持した予定ペン上げZへ同期移動します。現在位置が既にそれより高い場合は、ペンを下げないよう現在Zを維持します。


## 他のロボットへの移植

この章は COBOTTA 用の実装例です。文字処理は機種に依存しません。詳しくは[他のロボットでの利用](../other_robots.md)を参照してください。
