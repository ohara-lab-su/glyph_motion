# 輪郭・塗りつぶし・中心線 API

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

`height <= 0`、`curve_division < 1`、一文字APIへの複数文字指定、フォントに存在しない文字は `ValueError` です。

## FontGlyphFiller

```python
FontGlyphFiller(pixel_size: float, margin: float)
```

- `fill(outline_glyph: FontOutlineGlyph) -> FontFilledGlyph`

`pixel_size` は正値、`margin` は0以上が必要です。輪郭点が存在しない場合は `ValueError` です。

## FontCenterlineExtractor

```python
FontCenterlineExtractor()
```

- `extract(filled_glyph: FontFilledGlyph) -> FontCenterlineGlyph`

内部では `skimage.morphology.skeletonize()` を使い、8近傍グラフを端点・分岐点・閉路からパスへ分解します。

## FontCenterlineCleaner

```python
FontCenterlineCleaner(
    min_path_length: float,
    point_spacing: float,
)
```

- `clean(centerline_glyph: FontCenterlineGlyph) -> FontCenterlineGlyph`

連続重複点を除去し、指定長未満のパスを除外し、残ったパスを目標点間隔へ再サンプリングします。`min_path_length` は0以上、`point_spacing` は正値が必要です。
