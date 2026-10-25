# 通常フォントから中心線を作る

このチュートリアルでは、フォント輪郭を抽出し、塗りつぶし、中心線化し、ロボット向けに点列を整理します。

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

## パラメータの意味

`height` はフォントのunits per emに対する出力文字高さです。`curve_division` は2次・3次ベジェ曲線の分割数であり、大きいほど輪郭が滑らかになりますが、点数が増えます。

`pixel_size` は塗りつぶし格子の間隔です。小さくすると中心線の空間分解能は上がりますが、マスクとスケルトンの計算量が増えます。

`margin` は輪郭外側に確保する余白です。

`min_path_length` は除去する短い中心線枝のしきい値です。`point_spacing` は整理後の目標点間隔です。

## 結果の解釈

ここで得られる中心線は、フォント形状を画像処理した結果です。漢字本来の筆順ではありません。中心線の分岐構造や短い枝はフォント形状、格子間隔、スケルトン化結果に依存するため、`FontViewer` で必ず目視確認します。
