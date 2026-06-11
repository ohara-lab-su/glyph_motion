# README

## font_geometry.py
共通データ構造。主なクラスは FontPoint, FontOutlinePath, FontOutlineGlyph, FontFilledGlyph, FontCenterlinePath, FontCenterlineGlyph, FontStrokePath, FontStrokeGlyph, FontMotionCommand。

## font_outline_extractor.py
TTF/OTF/TTC からアウトラインを読む。主クラスは FontOutlineExtractor。

## font_fill_glyph.py
アウトラインを二値マスクへ塗りつぶす。主クラスは FontGlyphFiller。

## font_centerline_extractor.py
二値マスクからスケルトン中心線を取る。主クラスは FontCenterlineExtractor。

## font_centerline_cleaner.py
中心線の重複点除去、短線分除去、再サンプリング。主クラスは FontCenterlineCleaner。

## font_alphabet_stroke_builder.py
アルファベット用の仮 stroke 生成。主クラスは FontAlphabetStrokeBuilder。

## font_kanjivg_stroke_loader.py
KanjiVG SVG から筆順付き stroke を読む。本命寄り。主クラスは FontKanjiVGStrokeLoader, SvgPathSampler。

## font_viewer.py
各段階の表示。主クラスは FontViewer。表示対象は outline, filled, centerline, stroke。

