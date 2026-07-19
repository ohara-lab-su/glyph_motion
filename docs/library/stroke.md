# 筆順付きストローク API

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

文字列では各文字のadvance相当幅とspacingを用いてX方向へ配置します。SVGの `StrokePaths` グループ内のpath順を筆順として保持します。

## SvgPathSampler

```python
SvgPathSampler(curve_division: int)
```

- `sample_path(path_data: str) -> list[FontPoint]`

SVG pathの直線、水平・垂直線、2次・3次ベジェ、滑らかな曲線、閉路を点列化します。

## FontAlphabetStrokeBuilder

```python
FontAlphabetStrokeBuilder(
    height: float,
    spacing: float,
    stroke_division: int = 20,
)
```

- `build_text(text: str) -> FontStrokeGlyph`

対応文字は `A B C I L O T X Y Z` と空白です。小文字は大文字として処理します。
