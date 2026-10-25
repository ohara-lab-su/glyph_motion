# Installation and Prerequisites

The main dependencies used by the supplied implementation are:

```bash
pip install numpy matplotlib fonttools scikit-image
```

Writing with a physical COBOTTA robot additionally requires:

- `cobotta2`
- `x_logger`
- A COBOTTA environment capable of b-CAP communication
- KanjiVG SVG data

The standard-font pipeline requires a TTF, OTF, or TTC font containing the target characters. To select a font within a TTC collection, specify `font_number`.

For the KanjiVG pipeline, place the SVG file named after the character's Unicode code point, expressed as five lowercase hexadecimal digits, in the specified directory. For example, the character 島 uses `05cf6.svg`.

```text
kanjivg/
└── kanji/
    └── 05cf6.svg
```

## Import Examples

```python
from glyph_motion.lib.font_outline_extractor import FontOutlineExtractor
from glyph_motion.lib.font_fill_glyph import FontGlyphFiller
from glyph_motion.lib.font_centerline_extractor import FontCenterlineExtractor
from glyph_motion.lib.font_centerline_cleaner import FontCenterlineCleaner
from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader
from glyph_motion.lib.font_alphabet_stroke_builder import FontAlphabetStrokeBuilder
from glyph_motion.lib.font_viewer import FontViewer
```

The COBOTTA writing-class implementation imports the layout and robot-control classes from the following locations:

```python
from glyph_motion.font_line_layout import FontLineLayout
from cobotta2.cobotta_bcap import CobottaBcap
```
