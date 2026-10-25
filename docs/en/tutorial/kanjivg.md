# Creating Stroke-Ordered Paths from KanjiVG

The `StrokePaths` group in KanjiVG contains each stroke as an SVG path, ordered by stroke sequence. `FontKanjiVGStrokeLoader` preserves this order when generating `FontStrokeGlyph`.

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

## SVG filenames

SVG files are located using the Unicode code point of the target character. For example, `島` is U+5CF6, so its filename is `05cf6.svg`.

## Coordinate transformation

The loader reads the SVG `viewBox` and scales the coordinates to the specified `height`. It also converts SVG's downward-pointing Y coordinates into the coordinate system used for visualization and robotic processing.

## Supported path commands

`SvgPathSampler` processes the following SVG path commands:

- `M`, `m`
- `L`, `l`
- `H`, `h`
- `V`, `v`
- `Q`, `q`
- `T`, `t`
- `C`, `c`
- `S`, `s`
- `Z`, `z`

Quadratic and cubic Bézier curves are converted to point sequences according to `curve_division`.
