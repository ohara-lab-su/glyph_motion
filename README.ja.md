# glyph_motion

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/glyph_motion/blob/main/README.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/glyph_motion/blob/main/README.md)

[GitHub repository](https://github.com/ohara-lab-su/glyph_motion/) · [Project documentation](https://ohara-lab-su.github.io/)

`glyph_motion` は、フォントまたは KanjiVG 由来の筆順付きストロークをロボット書字用の移動命令へ変換し、COBOTTA b-CAP または ese774_frame 経由で実行するためのライブラリである。


## 構成

```text
glyph_motion/
  lib/
    font_*.py
  font_motion_builder.py
  font_robot_motion_builder.py
  font_robot_writer.py
  font_bcap_cobotta_writer.py
  server_fastapi/
    models/
    routers/
    clients/
    spec_writer.py
    server.py
examples/
  run_font_bcap_cobotta_writer_server.py
  client_write_text.py
```

`lib/` 以下は純粋なフォント処理層である。TTF/TTC、KanjiVG、輪郭、中心線、筆順付きストロークなどを扱い、ロボット固有処理を持たない。

`font_motion_builder.py` は、フォント由来のストロークまたは中心線をロボット非依存の相対移動命令へ変換する。

`font_robot_motion_builder.py` と `font_robot_writer.py` は、文字列をロボット書字向けの抽象命令列へ変換する層である。ペンアップ、ペンダウン、書字速度、移動速度、Z 方向退避量などを扱うが、COBOTTA 固有 API には依存しない。

`font_bcap_cobotta_writer.py` は、`CobottaBcap` を用いて抽象書字命令を COBOTTA b-CAP の相対 P 移動へ変換して実行する制御クラスである。

`server_fastapi/` は、`CobottaBcapFontWriter` を ese774_frame の透過 API として公開するサーバー層である。

## COBOTTA b-CAP 書字クラス

`CobottaBcapFontWriter` は、COBOTTA b-CAP を用いて任意文字列を書くためのクラスライブラリである。実行スクリプトではなく、ローカル利用、サーバー利用、テスト利用から呼び出すための制御クラスである。

主な API は以下である。

```text
connect()
prepare()
write_text(text, layout=None, execute=True)
preview_text(text, layout=None, max_commands=20)
halt()
reset_error()
disconnect()
get_current_position()
get_config()
set_config(values)
set_text_parameters(...)
set_motion_parameters(...)
set_origin_parameters(...)
set_transform_parameters(...)
```

`write_text()` は、文字列から筆順付きロボット命令を生成し、必要に応じて b-CAP 接続、TakeArm、MotorOn、加減速設定、開始姿勢準備を行ったうえで、`CobottaBcap.robo_dmove(..., coord_mode="P")` により実行する。

`preview_text()` は、ロボットへ投入せずに生成命令数と先頭命令の概要を返す。

## 設定

主要設定は `CobottaBcapFontWriterConfig` に集約される。

### 接続設定

```text
host
port
kanjivg_directory
```

### 文字生成設定

```text
layout
character_height_mm
character_spacing_mm
pen_lift_height_mm
curve_division
```

`character_height_mm` は一文字の高さである。`curve_division` は曲線分割数であり、大きくすると軌跡は滑らかになるが命令数は増える。

### モーション設定

```text
drawing_speed
travel_speed
pen_up_speed
pen_down_speed
approach_speed
accel
decel
move_interval_sec
max_travel_step_mm
skip_zero_move
zero_move_epsilon
```

`drawing_speed` は筆記中の XY 移動速度である。`travel_speed` は非筆記 XY 移動速度である。`pen_up_speed` と `pen_down_speed` は Z 方向の退避・接触動作に使う。`move_interval_sec` は各移動命令投入後の待ち時間であり、0.0 にすると投入間隔を詰める。`max_travel_step_mm` は非筆記時の大きな XY 移動を分割する上限である。

速度が遅い場合は、まず `travel_speed`、`drawing_speed`、`accel`、`decel`、`move_interval_sec`、`curve_division` を調整する。

### 原点・書字面設定

```text
origin_mode
surface_z_mode
robot_origin_x
robot_origin_y
robot_surface_z
approach_lift_height_mm
```

`origin_mode` は以下を想定する。

```text
current_as_first_stroke
current_as_origin
absolute_origin
```

`current_as_first_stroke` は、現在位置の XY を最初の筆画始点とみなす。初回の大きな XY 移動を抑制するため、実機調整時の既定値として扱う。

`current_as_origin` は、現在位置の XY を文字座標 `(0, 0)` とみなす。

`absolute_origin` は、`robot_origin_x` と `robot_origin_y` を文字座標 `(0, 0)` とみなす。

`surface_z_mode` は以下を想定する。

```text
current
absolute
```

`current` は現在 Z を書字面 Z とみなす。`absolute` は `robot_surface_z` を書字面 Z とみなす。

### 座標写像設定

```text
robot_x_sign
robot_y_sign
robot_z_sign
robot_x_scale
robot_y_scale
robot_z_scale
robot_drx
robot_dry
robot_drz
```

文字座標と COBOTTA P 座標の向き・倍率・姿勢差分を設定する。紙面の置き方、ペン姿勢、ロボット座標系に合わせて変更する。

## ese774_frame サーバー化

COBOTTA 文字書字処理は、通信量が少なく、画像転送のような連続大容量通信を必要としない。そのため、gRPC ではなく ese774_frame の FastAPI 透過 API として公開する。

公開オブジェクト名は以下である。

```text
cobotta_writer
```

公開 API は `server_fastapi/spec_writer.py` に定義する。

主な API は以下である。

```text
connect
prepare
disconnect
close
halt
reset_error
is_connected
get_current_position
get_config
set_config
set_text_parameters
set_motion_parameters
set_origin_parameters
set_transform_parameters
preview_text
write_text
```

サーバー起動例は `examples/run_font_bcap_cobotta_writer_server.py` に置く。クライアント例は `examples/client_write_text.py` に置く。

## 運用上の注意

実機で動作させる前に `preview_text()` で命令数と先頭命令を確認する。

初回調整では、`origin_mode="current_as_first_stroke"` と `surface_z_mode="current"` を使い、ペン先を最初の筆画始点かつ書字面に合わせてから実行する。

可動範囲外エラーが出る場合は、原点モード、文字サイズ、XY 符号、XY スケール、現在位置を確認する。

筆記が遅すぎる場合は、`move_interval_sec` を 0.0 にし、`travel_speed`、`drawing_speed`、`accel`、`decel` を上げる。曲線分割が過剰な場合は `curve_division` を下げる。

## 現行実装と他機種ロボットへの適用

**実装の確認事項。** 今回提供された COBOTTA 制御ソースは `glyph_motion/font_bcap_cobotta_writer.py` であり、`FontBcapCobottaWriter` と `FontBcapCobottaWriterConfig` を定義する。実際の書字入口は `FontBcapCobottaWriter.write(text, start_height_mm=None, return_to_start=None, new_line=None)` である。`connect()`、`disconnect()`、`set_params()`、`reset_error()`、`emergency_lift_pen()` なども実装されている。一方、このソースには、上記の従来の README に記載された `CobottaBcapFontWriter`、`write_text()`、`preview_text()` は定義されていない。従来の記述は情報を欠落させないため残しているが、添付された現行実装の API であることを保証するものではない。

本ライブラリの文字形状・レイアウト処理は **COBOTTA 専用ではない**。`glyph_motion.font_line_layout.FontLineLayout` はロボットに接続せずに配置済み文字と筆画点列を生成する。`glyph_motion.font_line_layout.PositionedCharacter` は配置済み筆画を保持し、`glyph_motion.lib.font_geometry.FontStrokePath` は筆画を表現する。`FontBcapCobottaWriter` は COBOTTA b-CAP による実行部分であり、文字・筆画生成の必須要素ではない。

### 他のロボットで使用する手順

1. `FontLineLayout` で文字列をレイアウトし、配置済み文字の筆画点列を取り出す。
2. 筆画点列を対象ロボットの単位・座標系に変換する。書字面原点、軸方向、ツール姿勢、動作範囲を定める。
3. 対象ロボットの制御クラスに、筆画始点へのペンアップ移動、筆画内のペンダウン描画、筆画間のペン退避を実装する。
4. 接続、サーボ有効化、速度・加減速、エラー処理、停止処理は対象ロボットの API で実装する。COBOTTA b-CAP の移動命令を他機種へそのまま流用しない。
5. ネットワーク制御が必要なら、**対象ロボット固有の制御クラス**をデバイスサーバーに公開する。添付された COBOTTA 実装の制御フロントは `font_bcap_cobotta_writer.py` であり、汎用筆画生成器とは区別する。サーバー公開 API はサーバー側ソースで別途確認する。
6. 実機で動かす前に、軌跡、座標変換、可動範囲、ペン退避量、緊急停止を検証する。

`docs/` 以下の詳細マニュアルは、README とは独立して管理する。
