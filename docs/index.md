# glyph_motion
view on [github](https://github.com/ohara-lab-su/glyph_motion/) / [ohara-lab-su (doc)](https://ohara-lab-su.github.io/)

`glyph_motion` は、文字を単なる画像として扱うのではなく、ロボットが実際になぞれる幾何データと筆画列へ変換するためのライブラリと
それを用いた、ロボットで文字を書くデバイスサーバーです

通常フォントの輪郭解析、二値領域化、中心線抽出、KanjiVGからの筆順付きストローク生成、
内蔵single-lineアルファベット生成、
処理結果の可視化、COBOTTAによる実書字を、それぞれ独立した段階として扱います。

---
```{toctree}
:maxdepth: 2
:caption: Contents:

api/modules
library/index
tutorial/alphabet
tutorial/cobotta
tutorial/font_to_centerline
tutorial/kanjivg
```
---


- [Home](index.md): index.md
- [思想とデータフロー](concepts.md): concepts.md
- [インストールと前提](installation.md): installation.md
- Tutorial:
    - [通常フォントから中心線を作る](tutorial/font_to_centerline.md): tutorial/font_to_centerline.md
    - [KanjiVGから筆順付きストロークを作る](tutorial/kanjivg.md): tutorial/kanjivg.md
    - [アルファベットストロークを作る](tutorial/alphabet.md): tutorial/alphabet.md
    - [COBOTTAで書字する](tutorial/cobotta.md): tutorial/cobotta.md
- API-Library:
    - [API概要](library/index.md): api/index.md
    - [輪郭・塗りつぶし・中心線](library/font_processing.md): api/font_processing.md
    - [筆順付きストローク](library/stroke.md): api/stroke.md
    - [表示](library/viewer.md): api/viewer.md
    - [COBOTTA書字](library/cobotta_writer.md): api/cobotta_writer.md
- [制約と注意事項](limitations.md): limitations.md

## このライブラリが解決する問題

一般的なフォントは、画面や印刷で文字を塗りつぶすための輪郭を持っています。一方、ペンを持つロボットに必要なのは、ペン先が通る線、筆画の順序、筆画間でペンを上げる位置、書字面上の絶対座標です。

この違いを吸収するため、本ライブラリは次の二つの入力経路を用意しています。

### 通常フォント経路

```text
TTF / OTF
  -> FontOutlineGlyph
  -> FontFilledGlyph
  -> FontCenterlineGlyph
  -> 整理済み中心線
```

輪郭フォントを任意の文字に利用できる点が利点です。ただし、画像処理で得られる中心線は、本来の筆順を意味しません。

### 筆順付きストローク経路

```text
KanjiVG SVG
  -> FontStrokeGlyph
  -> レイアウト
  -> ロボット書字
```

または、内蔵single-lineアルファベット定義から直接 `FontStrokeGlyph` を生成します。この経路では、各 `FontStrokePath` が一回ペンを下ろして描く単位であり、パス配列の順序が書字順です。

## 設計思想

処理段階を分離し、各クラスが一つの責務だけを担当します。輪郭抽出クラスは表示や中心線抽出を行わず、表示クラスはデータを変更しません。COBOTTA書字クラスも、文字形状の生成ではなく、配置済みストロークからロボット動作を実行する責務に限定されています。

この分離により、各段階を個別に可視化・検証でき、輪郭処理と筆順付き処理を混同せずに利用できます。

## 主な機能

- TTF／OTF／TTCからの文字輪郭抽出
- 輪郭内部の二値格子化
- スケルトン化と中心線パス抽出
- 短い枝の除去、重複点除去、再サンプリング
- KanjiVG SVGからの筆順付き漢字ストローク生成
- 内蔵single-lineアルファベット生成
- 各中間表現のMatplotlib表示
- 横書き・縦書き、反転、軸交換を考慮したCOBOTTA書字
- 筆画内描画と筆画間空走の分離
- 複数回の `write()` による継続書字と改行・改列

## ドキュメント構成

- [思想とデータフロー](concepts.md)
- [インストールと前提](installation.md)
- [通常フォントから中心線を作る](tutorial/font_to_centerline.md)
- [KanjiVGから筆順付きストロークを作る](tutorial/kanjivg.md)
- [アルファベットストロークを作る](tutorial/alphabet.md)
- [COBOTTAで書字する](tutorial/cobotta.md)
- [APIリファレンス](api/index.md)
- [制約と注意事項](limitations.md)

---
## 作者
- Kengo NAKADA (kengo.nakada@gmail.com)
