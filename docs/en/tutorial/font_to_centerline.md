# Creating Centerlines from Ordinary Fonts

This tutorial extracts font outlines, fills them, converts them to centerlines, and cleans the resulting point sequences for robotic use.

```python
from pathlib import Path

from glyph_motion.lib.font_outline_extractor import FontOutlineExtractor
from glyph_motion.lib.font_fill_glyph import FontGlyphFiller
from glyph_motion.lib.font_centerline_extractor import FontCenterlineExtractor
from glyph_motion.lib.font_centerline_cleaner import FontCenterlineCleaner
from glyph_motion.lib.font_viewer import FontViewer

font_file = Path("NotoSansCJKjp-Regular.otf")

outline_extractor = FontOutlineExtractor(
    font_file=font_file,
    height=40.0,
    curve_division=8,
)
outline = outline_extractor.extract_text(
    text="島",
    spacing=5.0,
)

filler = FontGlyphFiller(
    pixel_size=0.5,
    margin=2.0,
)
filled = filler.fill(outline_glyph=outline)

centerline_extractor = FontCenterlineExtractor()
raw_centerline = centerline_extractor.extract(
    filled_glyph=filled,
)

cleaner = FontCenterlineCleaner(
    min_path_length=1.0,
    point_spacing=2.0,
)
centerline = cleaner.clean(
    centerline_glyph=raw_centerline,
)

viewer = FontViewer()
viewer.show_filled_with_centerline(
    filled_glyph=filled,
    centerline_glyph=centerline,
)
```

## Parameter meanings

`height` is the output character height relative to the font's units per em. `curve_division` is the number of subdivisions for quadratic and cubic Bézier curves. Larger values produce smoother outlines but more points.

`pixel_size` is the spacing of the filling grid. Smaller values increase the spatial resolution of centerlines but also increase the computational cost of masks and skeletonization.

`margin` is the padding outside the outline.

`min_path_length` is the threshold for removing short centerline branches. `point_spacing` is the target spacing between points after cleanup.

## Interpreting the result

The resulting centerlines are produced by image processing of the font shape. They do **not** represent the original stroke order of kanji. Branch structure and short segments depend on font shape, grid spacing, and skeletonization results, so always inspect the result visually with `FontViewer`.
