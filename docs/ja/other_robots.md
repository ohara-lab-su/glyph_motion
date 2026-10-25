# 他のロボットでの利用と制御層の分離

`glyph_motion` の文字・筆画処理は COBOTTA 専用ではありません。文字の幾何情報と配置結果を生成する層と、ロボットを動かす層は別です。

## 確認できるクラスと役割

- `glyph_motion.lib.font_geometry.FontStrokePath`：筆画の点列を表現するデータ型。
- `glyph_motion.font_line_layout.FontLineLayout`：KanjiVG から文字を読み込み、文字セルへ配置する。ロボット接続やペン上下、速度制御は行いません。
- `glyph_motion.font_line_layout.PositionedCharacter`：文字と、配置後の `strokes` を保持します。
- `glyph_motion.font_bcap_cobotta_writer.FontBcapCobottaWriter`：COBOTTA 用の実機制御クラスです。`CobottaBcap` を使用し、絶対 P 座標へ変換して書字します。

## 他のロボットに対応する手順

1. `FontLineLayout` を使って文字列から配置済み筆画を生成します。返された各 `PositionedCharacter.strokes` を利用します。
2. 筆画内の点列を、使用するロボットの座標系・単位・書字面へ変換します。座標軸の符号、XY交換、原点、ツール姿勢、動作範囲をロボットごとに決定します。
3. 各筆画の開始前にペンを上げて始点へ移動し、ペンを下ろして筆画の点を順に描画します。筆画の終了時にはペンを上げ、次の筆画へ移動します。
4. ロボット固有の接続、アーム取得、サーボ有効化、速度・加減速設定、停止、エラー復旧は、ロボット用の制御クラスで実装します。
5. 必要に応じて、その制御クラスをデバイスサーバーに公開します。`FontBcapCobottaWriter` をそのまま別機種で使用できるという意味ではありません。
6. 実機投入前に、生成した点列、座標変換、作業範囲、ペン退避高さ、緊急停止を検証してください。

## COBOTTA とデバイスサーバー

添付された実装で確認できる COBOTTA 側の制御フロントは **`font_bcap_cobotta_writer.py`** の **`FontBcapCobottaWriter`** です。`connect()`、`set_params()`、`write()`、`disconnect()` などを実装しています。`write(text, start_height_mm=None, return_to_start=None, new_line=None)` は実機への書字処理であり、別ロボット向けに共通化された呼び出しではありません。

デバイスサーバー側の公開メソッド名やクライアント API は、サーバー実装の実ファイルで別途確認してください。ここでは、未確認の `write_text()` や `preview_text()` をこのクラスの実装済み API として扱いません。
