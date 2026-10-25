# 表示 API

## FontViewer

```python
viewer = FontViewer()
```

- `show_outline(outline_glyph) -> None`
- `show_filled(filled_glyph) -> None`
- `show_centerline(centerline_glyph) -> None`
- `show_stroke(stroke_glyph) -> None`
- `show_filled_with_centerline(filled_glyph, centerline_glyph) -> None`

表示クラスはデータ生成や変換を行いません。各処理段階を目視確認するための専用クラスです。表示時はXYの縮尺を等しくし、グリッドと軸ラベルを付けます。
