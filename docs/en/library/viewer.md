# Visualization API

## FontViewer

```python
viewer = FontViewer()
```

- `show_outline(outline_glyph) -> None`
- `show_filled(filled_glyph) -> None`
- `show_centerline(centerline_glyph) -> None`
- `show_stroke(stroke_glyph) -> None`
- `show_filled_with_centerline(filled_glyph, centerline_glyph) -> None`

The viewer does not generate or transform data. It is dedicated to visually inspecting each processing stage. The X and Y axes use equal scales, with a grid and axis labels.
