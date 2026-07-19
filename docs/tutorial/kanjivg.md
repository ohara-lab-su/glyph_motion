# KanjiVGから筆順付きストロークを作る

KanjiVGの `StrokePaths` グループには、各筆画がSVG pathとして筆順順に格納されています。`FontKanjiVGStrokeLoader` はこの順序を維持して `FontStrokeGlyph` を生成します。

```python
from pathlib import Path

from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader
from glyph_motion.lib.font_viewer import FontViewer

loader = FontKanjiVGStrokeLoader(
    kanjivg_directory=Path("kanjivg/kanji"),
    height=40.0,
    spacing=5.0,
    curve_division=20,
)

stroke_glyph = loader.load_text(text="島根")

print("stroke_count =", len(stroke_glyph))

viewer = FontViewer()
viewer.show_stroke(stroke_glyph=stroke_glyph)
```

## SVGファイル名

対象文字のUnicodeコードポイントからSVGファイルを検索します。「島」はU+5CF6であるため、ファイル名は `05cf6.svg` です。

## 座標変換

ローダーはSVGの `viewBox` を読み、指定した `height` に合わせてスケーリングします。また、SVGの下向きY座標を、表示・ロボット処理で扱う座標へ変換します。

## 対応するpath命令

`SvgPathSampler` は次のSVG path命令を処理します。

- `M`, `m`
- `L`, `l`
- `H`, `h`
- `V`, `v`
- `Q`, `q`
- `T`, `t`
- `C`, `c`
- `S`, `s`
- `Z`, `z`

2次・3次ベジェ曲線は `curve_division` に従って点列化されます。
