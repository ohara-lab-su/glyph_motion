# Changelog

このファイルでは、本プロジェクトの主要な変更履歴を記録する。


## [0.1.0] - KanjiVG ストロークを使って、cobotta で実際に文字を書く

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

## [0.0.2] - KanjiVG ストローク対応版

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

## [0.0.1] - 中心線生成パイプライン動作確認版

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
 
## [0.0.0] - 初期試作版

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