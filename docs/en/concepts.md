# Concepts and Data Flow

## Outlines and strokes are different

The paths in an outline font describe the outer contours and holes of characters. They indicate **where to fill**, not **in what order to move a pen**.

This library therefore distinguishes two types of data:

- `FontOutlineGlyph`, `FontFilledGlyph`, and `FontCenterlineGlyph`: data obtained by geometric processing of outline fonts.
- `FontStrokeGlyph`: stroke data that preserves stroke order and pen-down/pen-up units.

The centerline-extraction route prioritizes applicability to arbitrary fonts, whereas the KanjiVG route prioritizes natural stroke segmentation and stroke order for kanji.

## Intermediate representations

### FontOutlineGlyph

A collection of outline paths for one character or a string. Points are scaled to the specified character height. For multiple characters, the paths are placed along the X axis using the font's advance width and the specified `spacing`.

### FontFilledGlyph

A binary mask obtained by projecting outlines onto a grid at a fixed spacing. Multiple outlines are combined using XOR, allowing outer contours and inner holes to be distinguished.

### FontCenterlineGlyph

A collection of centerline paths obtained by skeletonizing the binary mask and tracing it as an 8-connected graph. Paths are split at branch points and endpoints.

### FontStrokeGlyph

A collection of ordered stroke paths. The path order is the writing order, and each `FontStrokePath` represents one continuous pen-down stroke.

## Separation of responsibilities

| Stage | Class | Main responsibility |
|---|---|---|
| Outline extraction | `FontOutlineExtractor` | Convert font instructions into point sequences and scale to the specified height |
| Filling | `FontGlyphFiller` | Convert outlines into a binary grid |
| Centerline extraction | `FontCenterlineExtractor` | Skeletonization and path tracing |
| Centerline cleanup | `FontCenterlineCleaner` | Remove short paths and duplicate points; resample paths |
| Kanji strokes | `FontKanjiVGStrokeLoader` | Preserve KanjiVG stroke order when producing point sequences |
| Alphabet strokes | `FontAlphabetStrokeBuilder` | Generate point sequences from built-in single-line characters |
| Visualization | `FontViewer` | Visually inspect intermediate representations |
| Physical writing | `FontBcapCobottaWriter` | Convert to absolute P coordinates and operate COBOTTA |

## Principles of robotic writing

COBOTTA distinguishes motion within a stroke from motion between strokes:

1. Move to the start of a stroke with the pen raised.
2. Lower the pen to the writing surface at the start point.
3. Submit consecutive points within the stroke at the same Z coordinate.
4. Raise the pen at the end of the stroke.
5. Move to the start of the next stroke.

Robot targets are absolute P coordinates referenced to the initial writing pose, not relative movements. The orientation components remain those of the initial pose; only XYZ is transformed from character coordinates.
