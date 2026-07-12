# Changelog

## v0.3.4 (2026-07-13)

- 累積bugfix

### Added

- take arm / give arm ... などの処理をまとめるのではなくて cobotta 等と同じく個別メソッドに変更

## v0.3.3 (2026-07-12)

### Added

- 文字列の縦書きに対応。
- 横書きと縦書きを切り替える `writing_direction` オプションを追加。
  - `horizontal`
  - `vertical`
- 縦書き時の文字進行方向を指定する `vertical_direction` オプションを追加。
  - `top_to_bottom`
  - `bottom_to_top`
- 書字中にエラーが発生した場合、現在の XY 座標と姿勢を維持したまま、Z 方向へペンを緊急退避する処理を追加。
- エラー発生後にコントローラのエラーを解除し、現在位置を再取得してからペンを退避する処理を追加。

### Changed

- 横書き時の進行方向を `line_direction`、縦書き時の進行方向を `vertical_direction` で個別に管理する構成へ変更。
- 横書きでは `workspace_width` と `cell_width`、縦書きでは `workspace_height` と `cell_height` から収容可能文字数を計算するよう変更。
- 書字方向に応じて、文字セルを X 軸方向または Y 軸方向へ配置するよう変更。
- 先頭文字は常に書字開始位置を基準とし、進行方向の指定では後続文字の配置方向だけを変更するよう整理。
- レイアウト関連オプションを変更した場合、新しい設定の検証に成功してから内部設定へ反映するよう変更。
- `write()` の実行中に、書字面から計算したペン上げ高さを緊急退避位置として保持するよう変更。
- 書字終了時または緊急退避後に、書字中状態と緊急退避位置を解除するよう変更。
- `write_server.py`、`client_write_text.py` および実行例に、横書き・縦書き・進行方向・反転などの各オプションを説明する一行コメントを追加。

### Fixed

- `writing_direction="vertical"` を指定しても、文字が横方向へ配置される場合があった問題を修正。
- 縦書き時にも横方向の作業領域から収容可能文字数を計算していた問題を修正。
- 縦書き時の文字進行方向を正しく切り替えられない問題を修正。
- `mirror_vertical` を指定しても、文字の上下反転が実際の座標へ反映されていなかった問題を修正。
- 横方向反転、上下方向反転、XY 軸交換および書字方向を組み合わせた場合の座標変換を修正。
- `set_config()` で不正なレイアウト設定を指定した場合、検証途中の設定だけが内部状態へ反映される問題を修正。
- `cell_width` が `workspace_width` を超える設定、および `cell_height` が `workspace_height` を超える設定を初期化時に検出するよう修正。
- `character_height` が `cell_height` を超える不正な設定を初期化時に検出するよう修正。
- 空文字列を指定した場合に、負の `start_height_mm` が検証されず正常終了する問題を修正。
- 書字途中でロボット動作が失敗した場合、ペンが書字面に接触した状態のまま終了処理へ進む問題を修正。
- 緊急退避時に現在位置が予定したペン上げ高さより高い場合、ペンを下げる方向へ移動する可能性があった問題を修正。
- `write()` の戻り値を確認せず、書字失敗を正常終了として扱う場合があった実行例を修正。

## v0.3.2 (2026-07-11)

### Changed

- `font_line_layout.py` および `font_bcap_cobotta_writer.py` の docstring を Google Style に統一し、公開ライブラリとして読みやすい構成へ整理。
- 文字レイアウト、座標変換、筆画生成、ペンの上下動作、ロボット動作について、設計意図やアルゴリズムが理解しやすいコメントを追加。
- `line_direction` の説明コメントを、実際の意味に合わせて文字の配置方向を示す内容へ修正。
- サンプルプログラムで `write()` の戻り値を確認し、書字失敗を検出できるよう改善。

### Fixed

- `mirror_vertical` が設定値として保持されるだけで、上下反転処理が実行されていなかった問題を修正。
- 縦書き時にも横方向の作業領域から収容文字数を計算していた問題を修正。
- 縦書き時は `workspace_height` と `cell_height` を用いて収容文字数を計算するよう修正。
- セルサイズが作業領域を超える不正なレイアウト設定を初期化時に検出するよう修正。
- 空文字列の場合に `start_height_mm` の入力値が検証されない問題を修正。
- `writing_direction` の選択肢判定の表記を整理。

## v0.3.1 (2026-07-10)

- 名前空間の調整
- **server_fastapi の v0.3.x 対応**
- param形を付け忘れいたのでそれを設定

## v0.3.0 (2026-07-10)

### Breaking Changes

- フォントからロボットへの書字処理を全面的に再設計しました。
- v0.2.x 系で実装していた書字パイプラインを廃止し、KanjiVG のストローク情報からロボット書字までの処理をシンプルな構成へ刷新しました。
- ストローク単位・文字空間単位を中心とした設計へ変更し、書字処理の責務を整理しました。

### Added

- 固定作業空間・固定文字空間による文字レイアウトを実装。
- 文字サイズと文字間隔を独立して設定可能に。
- `write()` 開始位置を基準とした書字方式を実装。
- `start_height_mm` を追加し、write() 開始位置が底面より上にある場合でも、その高さを基準として書字可能に。
- `return_to_start` により、書字終了後に開始位置へ復帰可能に。
- 空白文字 (`' '`) に対応。文字空間を確保しつつ描画を行わない動作を実装。
- 左右書字方向の切替に対応。
  - `left_to_right`
  - `right_to_left`
- 横書き・縦書きに対応。
- 左右反転（鏡写し）に対応。
- 上下反転に対応。
- XY 入れ替え（ロボット座標系の軸交換）に対応。

### Changed

- FontRobotWriter、FontMotionBuilder、FontRobotMotionBuilder を中心とした従来の書字処理を使用しない新しい書字方式へ変更。
- KanjiVG のストローク情報をそのまま利用し、文字空間へ配置する方式へ変更。
- ストローク内部は連続書字、ストローク間のみペンを上げて移動する構成へ整理。
- 書字開始・終了時のペン状態の扱いを整理。
- 文字配置処理とロボット座標変換処理を分離し、各種レイアウト設定を追加。
- 書字方向・文字反転・座標系変換を設定のみで切り替え可能な構成へ変更。

### Fixed

- v0.2.x 系では実質的に正常動作していなかったフォント書字処理を全面的に修正。
- 不要な中間処理を排除し、ストローク単位の書字動作へ改善。
- 書字開始位置および終了位置の扱いを修正。
- 空白文字を含む文字列の配置を修正。
- 文字方向・反転処理を組み合わせても正しくレイアウトされるよう修正。
- 
## v0.2.1 - pyi 生成 make.py と DeviceProxy 型定義生成を追加

### 追加

#### server_fastapi/make.py

ese774_frame の pyi 生成フレームを用いて、server_fastapi 配下の型定義ファイルを生成する `make.py` を追加した。

生成対象は以下である。

- `clients/async_cobotta_writer_client.pyi`
- `clients/sync_cobotta_writer_client.pyi`
- `clients/__init__.pyi`
- `routers/font_bcap_cobotta_writer_router.pyi`
- `__init__.pyi`

#### DeviceProxy 用 pyi 生成

DeviceProxy 登録に対応するため、`server_fastapi/__init__.pyi` の生成を追加した。

これにより、DeviceProxy から利用される公開クラス、API spec、alias 情報について、実装側の `__init__.py` と型定義側の `__init__.pyi` が揃うようにした。

### 変更

#### pyi 生成処理

client/router の pyi 生成を個別の手書き処理ではなく、ese774_frame 側の生成器を使う構成に整理した。

既存の client/router 実装を直接変更せず、生成対象と補正条件を `make.py` に集約した。

### 設計メモ

`font_bcap_cobotta_writer.py` は ctrl 側の実制御クラスとして維持し、`server_fastapi` 側では透過 API、client、router、DeviceProxy 登録、および pyi 生成のみを扱う構成とした。

これにより、制御本体と ese774_frame 依存のサーバー層を分離したまま、型補完に必要な pyi を生成できる。

## v0.2.0 - KanjiVG ストロークを使って、cobotta で実際に文字を書く (ese774 versiono)

### 追加
#### font_bcap_cobotta_writer.py

COBOTTA b-CAP を用いて任意文字列を書く制御クラス `CobottaBcapFontWriter` を追加した。

追加した主な機能は以下である。

- `CobottaBcap` を用いた b-CAP 接続、TakeArm、MotorOn、GiveArm、切断処理
- `FontRobotWriter` による文字列から筆順付きロボット命令列への変換
- `CobottaBcap.robo_dmove(..., coord_mode="P")` による相対 P 移動実行
- `write_text()` による任意文字列の書字
- `preview_text()` によるロボット非投入の命令確認
- `halt()` による停止
- `reset_error()` によるエラーリセット
- `get_current_position()` による現在 P 座標取得
- `get_config()` / `set_config()` による設定取得・更新
- 文字サイズ、文字間隔、ペンアップ高さ、曲線分割数の設定
- 描画速度、移動速度、ペンアップ速度、ペンダウン速度、アプローチ速度の設定
- 加速度、減速度、命令投入間隔、非筆記移動分割幅の設定
- 現在位置原点、最初の筆画始点原点、絶対原点の切替
- 現在 Z または絶対 Z による書字面設定
- 文字座標から COBOTTA P 座標への符号、倍率、姿勢差分の設定

#### server_fastapi/

`CobottaBcapFontWriter` を ese774_frame の透過 API として公開する FastAPI サーバー構成を追加した。

追加した主なファイルは以下である。

- `server_fastapi/spec_writer.py`
- `server_fastapi/server.py`
- `server_fastapi/models/common.py`
- `server_fastapi/models/writer.py`
- `server_fastapi/routers/font_bcap_cobotta_writer_router.py`
- `server_fastapi/clients/sync_cobotta_writer_client.py`
- `server_fastapi/clients/async_cobotta_writer_client.py`

公開 API は以下である。

- `connect`
- `prepare`
- `disconnect`
- `close`
- `halt`
- `reset_error`
- `is_connected`
- `get_current_position`
- `get_config`
- `set_config`
- `set_text_parameters`
- `set_motion_parameters`
- `set_origin_parameters`
- `set_transform_parameters`
- `preview_text`
- `write_text`

#### examples/

ese774_frame によるサーバー起動例とクライアント利用例を追加した。

追加した主なファイルは以下である。

- `examples/run_font_bcap_cobotta_writer_server.py`
- `examples/client_write_text.py`

### 変更

#### run_font_bcap_cobotta_writer.py

実行スクリプト内に直接置いていた COBOTTA b-CAP 書字処理を、`CobottaBcapFontWriter` を利用する薄い実行例へ整理した。

### 設計メモ

COBOTTA 文字書字処理は、文字列や設定値を API で渡し、文字生成、筆順展開、モーション生成、b-CAP 実行をサーバー側で完結させる構成とした。通信量が少なく、連続大容量データ転送を必要としないため、gRPC ではなく ese774_frame による FastAPI 透過 API 化を採用した。

### 動作確認

COBOTTA 実機で、少なくとも b-CAP 接続、TakeArm、MotorOn、`robo_dmove()` による文字書字動作を確認した。

### 既知の課題

- API 経由の連続書字時における排他制御は未整理である。
- 書字中の pause/resume は未実装である。
- 原点・書字面 Z の運用ルールは実機調整を通じてさらに整理する必要がある。
- 可動範囲外エラーを事前に検出する幾何チェックは未実装である。
- 軌跡の最適化、筆画間移動の最短化、速度プロファイル最適化は未実装である。

## v0.1.0 - KanjiVG ストロークを使って、cobotta で実際に文字を書く

cobotta2 モジュールを用いる

### font_motion_builder.py

フォントのストロークデータをロボット非依存の相対移動命令列へ変換する機能を追加した。

機能:
- ストロークごとの相対移動生成
- 曲線分割
- ペンアップ移動の生成
- 文字サイズ指定
- 文字間隔指定

### font_robot_motion_builder.py

ロボット向け書字命令への変換層を追加した。

機能:
- FontMotionCommand を FontRobotMotionCommand へ変換
- ペンアップ／ペンダウン状態管理
- 書字速度・移動速度設定
- Z方向退避量設定

### font_robot_writer.py

文字列からロボット書字命令列を生成する高水準 API を追加した。

機能:
- 横書き
- 縦書き
- KanjiVG を利用した筆順生成
- 文字列全体の命令列生成

### run_font_bcap_cobotta_writer.py

COBOTTA b-CAP を用いた実行サンプルを追加した。

機能:
- FontRobotMotionCommand の実行
- CobottaBcap.robo_dmove() による高速相対移動
- TakeArm / MotorOn / GiveArm の実行
- 速度・加減速設定
- KanjiVG ディレクトリ設定
- Dry Run モード
---

## v0.0.2 - KanjiVG ストローク対応版

### 追加

#### font_stroke_builder.py

筆順付きストロークデータを扱うための処理を追加した。

機能:

- FontStrokeGlyph 生成
- FontStrokePath 管理
- 筆画単位のデータ管理
- アルファベット用ストローク定義

#### font_kanjivg_stroke_loader.py

KanjiVG SVG から筆順付きストロークを読み込む処理を追加した。

機能:

- KanjiVG SVG 読み込み
- SVG Path 解析
- SVG 座標変換
- 二次ベジェ曲線対応
- 三次ベジェ曲線対応
- 筆順保持
- FontStrokeGlyph 生成

#### run_font_kanjivg_stroke_test.py

KanjiVG ストローク表示確認用スクリプトを追加した。

機能:

- KanjiVG 読み込み確認
- Stroke 表示確認
- 筆順確認

#### run_font_kanjivg_motion_test.py

KanjiVG ストロークからモーション生成を確認するスクリプトを追加した。

機能:

- KanjiVG 読み込み
- Motion 生成
- Motion 表示

### 変更

#### font_geometry.py

筆順付きストローク表現を追加した。

追加したデータ構造:

- FontStrokePath
- FontStrokeGlyph

#### font_motion_builder.py

中心線だけでなくストロークデータからもモーション生成できるように変更した。

追加:

- build_from_stroke()

対応入力:

```text
FontCenterlineGlyph
FontStrokeGlyph
```

## v0.0.1 - 中心線生成パイプライン動作確認版

### 追加

#### font_viewer.py

処理パイプライン全体を目視確認できる統合確認処理を追加した。

確認可能な工程:

- FontOutlineGlyph
- FontFilledGlyph
- FontCenterlineGlyph
- Filled + Centerline 重ね表示

#### font_centerline_cleaner.py

中心線抽出後の後処理を正式にパイプラインへ組み込んだ。

機能:

- 重複点除去
- 短線分除去
- 点列再サンプリング
- 点間隔均一化

#### font_motion_builder.py

中心線整理済みデータを入力として扱う構成へ変更した。

機能:

- FontCenterlineCleaner の注入対応
- 中心線整理後のモーション生成
- 中心線再構築機能

### 変更

#### font_outline_extractor.py

TrueType Collection (TTC) フォントへ対応した。

追加:

- font_number 指定
- TTC 内フォント選択

macOS 標準フォントを直接利用可能となった。

#### font_viewer.py

単体表示テストからパイプライン確認テストへ変更した。

変更前:

```text
Outline
↓
Filled
```

変更後:

```text
Outline
↓
Filled
↓
Centerline
↓
Filled + Centerline
```

### 動作確認

macOS 環境にて以下を確認した。

- ヒラギノ角ゴシック TTC 読み込み
- フォント輪郭抽出
- 文字領域生成
- スケルトン化
- 中心線抽出
- 中心線整理
- 描画表示

### 現在の処理フロー

```text
FontOutlineExtractor
↓
FontGlyphFiller
↓
FontCenterlineExtractor
↓
FontCenterlineCleaner
↓
FontMotionBuilder
```

### 現在の到達点

本バージョンでは、

```text
フォント
↓
輪郭
↓
塗りつぶし
↓
中心線
↓
モーション命令
```

までの基本パイプラインが動作することを確認した。

### 現在の制限事項

- 中心線はスケルトン化ベース
- 筆順情報は存在しない
- ストローク構造は復元しない
- 分岐部で不自然な線が発生する場合がある
- Path の接続順序最適化は未実装
- ペン移動経路最適化は未実装
- ロボット固有座標系への変換は未実装
- Z軸制御は未実装

### 次版予定

- FontMotionBuilder の改善
- Path 接続順序最適化
- ペンアップ移動最短化
- 中心線品質向上
- 日本語漢字での品質評価
- アウトライン直接中心線化アルゴリズムの検討
- ロボット制御系との接続
 
## v0.0.0 - 初期試作版

### 追加

#### font_geometry.py

フォント処理全体で共有するデータ構造を実装した。

追加したデータ構造:

- `FontPoint`
- `FontOutlinePath`
- `FontOutlineGlyph`
- `FontFilledGlyph`
- `FontCenterlinePath`
- `FontCenterlineGlyph`
- `FontMotionCommand`

#### font_outline_extractor.py

フォントファイルから文字輪郭を取得する処理を実装した。

機能:

- TrueType/OpenType フォントの読み込み
- グリフ輪郭の取得
- 二次ベジェ曲線の点列化
- 三次ベジェ曲線の点列化
- 文字列全体の輪郭抽出
- フォントサイズ変換

#### font_fill_glyph.py

輪郭データから塗りつぶし済み文字領域を生成する処理を実装した。

機能:

- 輪郭内判定
- 二値マスク生成
- 内部空洞を含む文字領域生成
- ピクセルサイズ指定
- マージン指定

#### font_centerline_extractor.py

塗りつぶし済み文字領域から中心線を抽出する処理を実装した。

機能:

- スケルトン化
- 8近傍グラフ生成
- 分岐点検出
- 中心線パス抽出

#### font_centerline_cleaner.py

抽出した中心線をロボット向けに整理する処理を実装した。

機能:

- 重複点除去
- 短い線分除去
- 点列再サンプリング
- 点間隔の均一化

#### font_motion_builder.py

中心線を XY 相対移動命令へ変換する処理を実装した。

機能:

- ペンアップ命令生成
- ペンダウン命令生成
- XY 相対移動命令生成
- 中心線復元機能

#### font_viewer.py

処理途中のデータを目視確認するための表示機能を実装した。

機能:

- 輪郭表示
- 塗りつぶし表示
- 中心線表示
- 塗りつぶし＋中心線重ね表示

### 処理フロー

現在の処理フローは以下である。

```text
FontOutlineExtractor

↓

FontGlyphFiller

↓

FontCenterlineExtractor

↓

FontCenterlineCleaner

↓

FontMotionBuilder
```

### 目的

一般的な TrueType/OpenType フォントから文字形状を取得し、

ロボットが文字を書くための中心線データおよび移動命令へ変換するための基盤ライブラリとして開発を開始した。

### 現在の制限事項

- 中心線抽出はラスター化後のスケルトン化に依存している
- 筆順は復元しない
- 書道的なストローク構造は復元しない
- フォントによって中心線品質が変化する
- 分岐部で不要な短線分が発生する場合がある
- 線分接続順序の最適化は未実装
- 移動経路最適化は未実装
- ロボット固有フォーマット出力は未実装

### 今後の予定

- 中心線品質向上
- 分岐除去アルゴリズム追加
- 線分接続最適化
- 移動経路最適化
- 複数フォントでの検証
- 日本語文字品質評価
- アウトラインから直接中心線を求める方式の検討
- ロボット制御ライブラリとの接続