# Creating Alphabet Strokes

`FontAlphabetStrokeBuilder` generates `FontStrokeGlyph` directly from built-in single-line definitions, without using outline fonts.

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

Lowercase letters are converted to uppercase before processing. A space advances the position by one character width plus `spacing`.

## Currently defined characters

```text
A B C I L O T X Y Z
```

Passing an undefined character raises `ValueError`.

## stroke_division

The built-in characters are defined using sparse control points. Each line segment is divided into `stroke_division` equal subsegments. This adjusts the density of points passed to the robot without changing downstream processing.

Character width is `height * 0.7`. The position of the next character is determined by this width plus `spacing`.
