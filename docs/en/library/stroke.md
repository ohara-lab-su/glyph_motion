# Stroke-Order API

## FontKanjiVGStrokeLoader

```python
FontKanjiVGStrokeLoader(
    kanjivg_directory: Path,
    height: float,
    spacing: float,
    curve_division: int = 16,
)
```

- `load_text(text: str) -> FontStrokeGlyph`
- `load_character(character: str) -> tuple[FontStrokeGlyph, float]`

For a string, characters are positioned along the X axis using their advance-equivalent widths and `spacing`. The path order within the SVG `StrokePaths` group is preserved as stroke order.

## SvgPathSampler

```python
SvgPathSampler(curve_division: int)
```

- `sample_path(path_data: str) -> list[FontPoint]`

Converts SVG path commands for lines, horizontal and vertical lines, quadratic and cubic Bézier curves, smooth curves, and closed paths into point sequences.

## FontAlphabetStrokeBuilder

```python
FontAlphabetStrokeBuilder(
    height: float,
    spacing: float,
    stroke_division: int = 20,
)
```

- `build_text(text: str) -> FontStrokeGlyph`

Supported characters are `A B C I L O T X Y Z` and spaces. Lowercase letters are processed as uppercase.
