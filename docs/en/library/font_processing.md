# Outline, Filling, and Centerline API

## FontOutlineExtractor

```python
FontOutlineExtractor(
    font_file: Path,
    height: float,
    curve_division: int,
    font_number: int = 0,
)
```

- `extract_text(text: str, spacing: float) -> FontOutlineGlyph`
- `extract_character(character: str) -> FontOutlineGlyph`

A `ValueError` is raised for `height <= 0`, `curve_division < 1`, passing multiple characters to the single-character API, or a character not present in the font.

## FontGlyphFiller

```python
FontGlyphFiller(pixel_size: float, margin: float)
```

- `fill(outline_glyph: FontOutlineGlyph) -> FontFilledGlyph`

`pixel_size` must be positive and `margin` must be nonnegative. A `ValueError` is raised when no outline points are present.

## FontCenterlineExtractor

```python
FontCenterlineExtractor()
```

- `extract(filled_glyph: FontFilledGlyph) -> FontCenterlineGlyph`

Internally, it uses `skimage.morphology.skeletonize()` and decomposes an 8-connected graph into paths at endpoints, branch points, and loops.

## FontCenterlineCleaner

```python
FontCenterlineCleaner(
    min_path_length: float,
    point_spacing: float,
)
```

- `clean(centerline_glyph: FontCenterlineGlyph) -> FontCenterlineGlyph`

Consecutive duplicate points are removed, paths shorter than the specified length are discarded, and the remaining paths are resampled at the target point spacing. `min_path_length` must be nonnegative and `point_spacing` must be positive.
