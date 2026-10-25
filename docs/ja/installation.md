# インストールと前提

添付実装で使用されている主要依存関係は次のとおりです。

```bash
pip install numpy matplotlib fonttools scikit-image
```

COBOTTA実機書字には、別途次が必要です。

- `cobotta2`
- `x_logger`
- b-CAP通信が可能なCOBOTTA環境
- KanjiVG SVGデータ

通常フォント経路には、対象文字を含むTTF、OTF、またはTTCフォントが必要です。TTC内のフォントを選択する場合は `font_number` を指定します。

KanjiVG経路では、文字のUnicodeコードポイントを小文字16進数5桁で表したSVGファイルを、指定ディレクトリへ配置します。例として「島」は `05cf6.svg` です。

```text
kanjivg/
└── kanji/
    └── 05cf6.svg
```

## インポート例

```python
from glyph_motion.lib.font_outline_extractor import FontOutlineExtractor
from glyph_motion.lib.font_fill_glyph import FontGlyphFiller
from glyph_motion.lib.font_centerline_extractor import FontCenterlineExtractor
from glyph_motion.lib.font_centerline_cleaner import FontCenterlineCleaner
from glyph_motion.lib.font_kanjivg_stroke_loader import FontKanjiVGStrokeLoader
from glyph_motion.lib.font_alphabet_stroke_builder import FontAlphabetStrokeBuilder
from glyph_motion.lib.font_viewer import FontViewer
```

COBOTTA書字クラスの実装では、次の位置からレイアウトとロボット制御を読み込みます。

```python
from glyph_motion.font_line_layout import FontLineLayout
from cobotta2.cobotta_bcap import CobottaBcap
```
