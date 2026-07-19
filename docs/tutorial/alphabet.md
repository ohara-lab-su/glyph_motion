# アルファベットストロークを作る

`FontAlphabetStrokeBuilder` は、輪郭フォントを使わず、内蔵されたsingle-line定義から直接 `FontStrokeGlyph` を生成します。

```python
from glyph_motion.lib.font_alphabet_stroke_builder import FontAlphabetStrokeBuilder
from glyph_motion.lib.font_viewer import FontViewer

builder = FontAlphabetStrokeBuilder(
    height=40.0,
    spacing=5.0,
    stroke_division=20,
)

stroke_glyph = builder.build_text(text="ABC")

viewer = FontViewer()
viewer.show_stroke(stroke_glyph=stroke_glyph)
```

小文字は大文字へ変換して処理されます。空白は一文字分の幅とspacingを進めます。

## 現在定義されている文字

```text
A B C I L O T X Y Z
```

未定義文字を渡すと `ValueError` になります。

## stroke_division

内蔵文字は粗い制御点で定義されています。各線分は `stroke_division` 個の小区間へ等分されます。これにより、後段を変更せずにロボットへ渡す点列密度を調整できます。

文字幅は `height * 0.7` です。文字列内の次文字位置は、この幅と `spacing` の和で決まります。
