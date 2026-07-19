# 思想とデータフロー

## 輪郭と筆画は異なる

輪郭フォントのパスは、文字の外周と穴を表します。これは「どこを塗るか」を示すデータであり、「どの順番でペンを動かすか」を示す筆画データではありません。

そのため本ライブラリは、次の二つを明確に区別します。

- `FontOutlineGlyph`、`FontFilledGlyph`、`FontCenterlineGlyph`: 輪郭フォントを幾何処理して得るデータ
- `FontStrokeGlyph`: 筆順とペン上下単位を持つストロークデータ

中心線抽出経路は任意フォントへの適用性を優先し、KanjiVG経路は漢字の筆順と自然な筆画分割を優先します。

## 中間表現

### FontOutlineGlyph

一文字または文字列の輪郭パス群です。各点は指定した文字高さへスケーリングされます。複数文字の場合は、フォントのadvance widthと指定spacingでX方向へ配置されます。

### FontFilledGlyph

輪郭を一定間隔の格子へ投影した二値マスクです。複数輪郭はXORで合成されるため、外周と内側の穴を区別できます。

### FontCenterlineGlyph

二値マスクをスケルトン化し、8近傍グラフとして追跡した中心線パス群です。分岐点や端点でパスが分割されます。

### FontStrokeGlyph

筆順付きパス群です。パス順が書字順であり、一つの `FontStrokePath` は一回ペンを下ろして描く単位です。

## 分解された責務

| 段階 | クラス | 主な責務 |
|---|---|---|
| 輪郭抽出 | `FontOutlineExtractor` | フォント命令を点列化し、指定高さへ変換 |
| 塗りつぶし | `FontGlyphFiller` | 輪郭を二値格子へ変換 |
| 中心線抽出 | `FontCenterlineExtractor` | スケルトン化とパス追跡 |
| 中心線整理 | `FontCenterlineCleaner` | 短線除去、重複点除去、再サンプリング |
| 漢字ストローク | `FontKanjiVGStrokeLoader` | KanjiVGの筆画順を保持して点列化 |
| 英字ストローク | `FontAlphabetStrokeBuilder` | 内蔵single-line文字から点列生成 |
| 表示 | `FontViewer` | 中間表現の目視確認 |
| 実書字 | `FontBcapCobottaWriter` | 絶対P座標変換とCOBOTTA動作 |

## ロボット書字の原則

COBOTTA書字では、筆画内と筆画間で動作を分けます。

1. ペンを上げた状態で筆画始点へ空走する。
2. 始点で書字面までペンを下ろす。
3. 同一Z座標上で筆画内の点を連続投入する。
4. 筆画終点でペンを上げる。
5. 次の筆画始点へ移動する。

ロボット目標は相対移動ではなく、書字開始姿勢を基準にした絶対P座標です。姿勢成分は開始姿勢を維持し、XYZだけを文字座標から変換します。
