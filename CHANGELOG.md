# Changelog

## v0.3.6, 2026-07-28, nakada

- After setting up cobotta3/4.

## v0.3.5 (2026-07-15), nakada

### Added

- Added the ability to retain the previous writing state across consecutive calls to `write()`, allowing writing to resume from where the previous call left off.
- Added the `new_line` option to start the next `write()` call on a new line (or column).
- Added `set_new_line()` to configure the default line-break behavior.
- Added `set_start_height_mm()` to configure the default pen descent distance at the start of `write()`.
- Added `set_pen_lift_mm()` to configure the default pen clearance height during and after writing.
- Added `set_return_to_start()` to configure whether the pen returns to the starting position after writing.
- Added options for specifying the line-break direction for horizontal and vertical writing:
  - `horizontal_new_line_direction`
    - `top_to_bottom`
    - `bottom_to_top`
  - `vertical_new_line_direction`
    - `right_to_left`
    - `left_to_right`

### Changed

- Changed `start_height_mm`, `pen_lift_mm`, `return_to_start`, and `new_line` in `write()` to use instance defaults when omitted and explicitly supplied values when provided.
- When line-break direction options are omitted, the direction is now determined automatically from the existing layout and character-mirroring settings.
- With `return_to_start=False`, the logical starting position for the next character is retained instead of the physical position where writing ended, enabling natural continuation across `write()` calls.

### Fixed

- Fixed cases in which settings were not carried over correctly after the addition of line-break functionality.
- Clarified the precedence of `set_params()`, individual setters, and `write()` arguments to ensure consistent behavior.

## v0.3.4 (2026-07-13)

- Cumulative bug fixes.

### Added

- Changed operations such as take arm and give arm from grouped operations to individual methods, as in cobotta.

## v0.3.3 (2026-07-12), nakada

### Added

- Added support for vertical text layout.
- Added `writing_direction` to select horizontal or vertical writing:
  - `horizontal`
  - `vertical`
- Added `vertical_direction` to specify character progression in vertical writing:
  - `top_to_bottom`
  - `bottom_to_top`
- Added emergency pen retraction along the Z axis if an error occurs during writing, while preserving the current XY coordinates and orientation.
- Added a procedure to clear controller errors, retrieve the current position, and then retract the pen after an error.

### Changed

- Separated character progression settings into `line_direction` for horizontal writing and `vertical_direction` for vertical writing.
- Changed character capacity calculations to use `workspace_width` and `cell_width` for horizontal writing, and `workspace_height` and `cell_height` for vertical writing.
- Changed character-cell placement to proceed along the X or Y axis according to the writing direction.
- The first character is always positioned relative to the writing start position; progression direction now affects only the placement of subsequent characters.
- Layout changes are now applied to internal settings only after the new configuration passes validation.
- During `write()`, the pen-up height calculated from the writing surface is retained as the emergency retraction position.
- The writing-in-progress state and emergency retraction position are cleared after writing ends or emergency retraction completes.
- Added one-line comments explaining horizontal and vertical writing, progression directions, mirroring, and other options to `write_server.py`, `client_write_text.py`, and usage examples.

### Fixed

- Fixed cases where characters were arranged horizontally even with `writing_direction="vertical"`.
- Fixed character capacity being calculated from the horizontal workspace during vertical writing.
- Fixed incorrect switching of character progression direction in vertical writing.
- Fixed `mirror_vertical` not affecting actual coordinates despite being specified.
- Corrected coordinate transformations combining horizontal mirroring, vertical mirroring, XY-axis swapping, and writing direction.
- Fixed `set_config()` applying partially validated settings to internal state when an invalid layout configuration was provided.
- Added initialization checks for `cell_width` exceeding `workspace_width` and `cell_height` exceeding `workspace_height`.
- Added an initialization check for `character_height` exceeding `cell_height`.
- Fixed negative `start_height_mm` values going unvalidated when an empty string was supplied.
- Fixed cases where robot motion failed during writing and cleanup began while the pen was still touching the writing surface.
- Fixed emergency retraction potentially moving the pen downward when the current position was already higher than the planned pen-up height.
- Fixed examples that treated failed writing as successful because they did not check the return value of `write()`.

## v0.3.2 (2026-07-11), nakada

### Changed

- Standardized docstrings in `font_line_layout.py` and `font_bcap_cobotta_writer.py` to Google Style to improve readability as a public library.
- Added comments explaining the design intent and algorithms for character layout, coordinate transformations, stroke generation, pen lifting and lowering, and robot motion.
- Corrected the explanation of `line_direction` to indicate character placement direction.
- Updated example programs to check the return value of `write()` and detect writing failures.

### Fixed

- Fixed `mirror_vertical` being stored as a setting without actually applying vertical mirroring.
- Fixed character capacity being calculated from the horizontal workspace even during vertical writing.
- Changed vertical-writing capacity calculations to use `workspace_height` and `cell_height`.
- Added initialization checks for invalid layouts where cell dimensions exceed the workspace.
- Fixed `start_height_mm` not being validated for empty strings.
- Clarified the handling of valid `writing_direction` values.

## v0.3.1 (2026-07-10), nakada

- Adjusted namespaces.
- **Updated `server_fastapi` for v0.3.x.**
- Added a missing parameter format specification.

## v0.3.0 (2026-07-10), nakada

### Breaking Changes

- Completely redesigned the font-to-robot writing process.
- Replaced the v0.2.x writing pipeline with a simpler design that converts KanjiVG stroke data into robot writing motions.
- Reorganized writing responsibilities around strokes and character-space units.

### Added

- Implemented character layout using fixed workspaces and character cells.
- Allowed character size and spacing to be configured independently.
- Implemented writing relative to the starting position of `write()`.
- Added `start_height_mm`, allowing writing relative to a start position above the writing surface.
- Added `return_to_start` to return to the starting position after writing.
- Added support for spaces (`' '`), which occupy a character cell without drawing.
- Added left-to-right and right-to-left writing:
  - `left_to_right`
  - `right_to_left`
- Added horizontal and vertical writing.
- Added horizontal mirroring.
- Added vertical mirroring.
- Added XY-axis swapping for robot coordinate transformations.

### Changed

- Replaced the previous writing approach centered on `FontRobotWriter`, `FontMotionBuilder`, and `FontRobotMotionBuilder`.
- Changed to a method that places KanjiVG stroke data directly into character cells.
- Organized motion so that the pen stays down within a stroke and is raised only between strokes.
- Clarified pen-state handling at the start and end of writing.
- Separated character placement from robot coordinate transformations and added layout settings.
- Made writing direction, character mirroring, and coordinate transformations configurable through settings alone.

### Fixed

- Completely revised font writing, which had not functioned properly in practice in v0.2.x.
- Removed unnecessary intermediate processing and improved stroke-based writing.
- Corrected the handling of writing start and end positions.
- Corrected the placement of strings containing spaces.
- Corrected layout when combining writing direction and mirroring.

## v0.2.1 - Added `make.py` for pyi generation and DeviceProxy type-definition generation, nakada

### Added

#### server_fastapi/make.py

Added `make.py` to generate type-definition files under `server_fastapi` using the pyi generation framework provided by `ese774_frame`.

Generated files:

- `clients/async_cobotta_writer_client.pyi`
- `clients/sync_cobotta_writer_client.pyi`
- `clients/__init__.pyi`
- `routers/font_bcap_cobotta_writer_router.pyi`
- `__init__.pyi`

#### DeviceProxy pyi generation

Added generation of `server_fastapi/__init__.pyi` to support DeviceProxy registration.

This aligns the implementation-side `__init__.py` and type-definition-side `__init__.pyi` for public classes, API specifications, and aliases exposed through DeviceProxy.

### Changed

#### pyi generation

Replaced individually handwritten client/router pyi generation with the generators provided by `ese774_frame`.

Centralized generation targets and adjustment conditions in `make.py` without directly modifying existing client/router implementations.

### Design Notes

`font_bcap_cobotta_writer.py` remains the actual controller class. The `server_fastapi` layer handles only the transparent API, clients, router, DeviceProxy registration, and pyi generation.

This keeps the controller implementation separate from the `ese774_frame`-dependent server layer while allowing generation of pyi files for type completion.

## v0.2.0 - Writing actual characters with COBOTTA using KanjiVG strokes (ese774 version)

### Added

#### font_bcap_cobotta_writer.py

Added `CobottaBcapFontWriter`, a control class for writing arbitrary text using COBOTTA b-CAP.

Main features:

- b-CAP connection, TakeArm, MotorOn, GiveArm, and disconnection using `CobottaBcap`.
- Conversion of text into ordered robot writing commands using `FontRobotWriter`.
- Execution of relative P-coordinate movements using `CobottaBcap.robo_dmove(..., coord_mode="P")`.
- Writing arbitrary text with `write_text()`.
- Previewing commands without sending them to the robot with `preview_text()`.
- Stopping with `halt()`.
- Resetting errors with `reset_error()`.
- Retrieving the current P coordinates with `get_current_position()`.
- Retrieving and updating configuration with `get_config()` / `set_config()`.
- Configuration of character size, character spacing, pen-up height, and curve subdivision count.
- Configuration of drawing speed, travel speed, pen-up speed, pen-down speed, and approach speed.
- Configuration of acceleration, deceleration, command submission interval, and non-writing travel segment length.
- Switching between the current-position origin, first-stroke-start origin, and absolute origin.
- Setting the writing surface relative to the current Z or an absolute Z coordinate.
- Configuring signs, scaling, and orientation offsets when converting character coordinates to COBOTTA P coordinates.

#### server_fastapi/

Added a FastAPI server configuration that exposes `CobottaBcapFontWriter` through the transparent API provided by `ese774_frame`.

Main files added:

- `server_fastapi/spec_writer.py`
- `server_fastapi/server.py`
- `server_fastapi/models/common.py`
- `server_fastapi/models/writer.py`
- `server_fastapi/routers/font_bcap_cobotta_writer_router.py`
- `server_fastapi/clients/sync_cobotta_writer_client.py`
- `server_fastapi/clients/async_cobotta_writer_client.py`

Public APIs:

- `connect`
- `prepare`
- `disconnect`
- `close`
- `halt`
- `reset_error`
- `is_connected`
- `get_current_position`
- `get_config`
- `set_config`
- `set_text_parameters`
- `set_motion_parameters`
- `set_origin_parameters`
- `set_transform_parameters`
- `preview_text`
- `write_text`

#### examples/

Added examples for starting a server and using a client through `ese774_frame`.

Main files added:

- `examples/run_font_bcap_cobotta_writer_server.py`
- `examples/client_write_text.py`

### Changed

#### run_font_bcap_cobotta_writer.py

Refactored the COBOTTA b-CAP writing logic previously embedded directly in the executable script into a thin example using `CobottaBcapFontWriter`.

### Design Notes

The COBOTTA writing system accepts text and configuration through an API; character generation, stroke-order expansion, motion generation, and b-CAP execution are all performed on the server. Since communication volume is small and continuous high-volume transfers are unnecessary, the FastAPI transparent API provided by `ese774_frame` was selected instead of gRPC.

### Verification

Confirmed at least b-CAP connection, TakeArm, MotorOn, and character writing with `robo_dmove()` on a physical COBOTTA robot.

### Known Issues

- Exclusive access control during consecutive writing operations through the API has not been finalized.
- Pause/resume during writing is not implemented.
- Rules for managing origins and the writing-surface Z coordinate require further refinement through physical testing.
- Geometric prechecks for out-of-range motion errors are not implemented.
- Trajectory optimization, minimization of travel between strokes, and speed-profile optimization are not implemented.

## v0.1.0 - Writing actual characters with COBOTTA using KanjiVG strokes

Uses the `cobotta2` module.

### font_motion_builder.py

Added conversion of font stroke data into robot-independent relative motion commands.

Features:
- Generation of relative movements for each stroke.
- Curve subdivision.
- Generation of pen-up movements.
- Character size configuration.
- Character spacing configuration.

### font_robot_motion_builder.py

Added a conversion layer for robot writing commands.

Features:
- Conversion of `FontMotionCommand` to `FontRobotMotionCommand`.
- Pen-up/pen-down state management.
- Writing and travel speed settings.
- Z-axis retraction distance settings.

### font_robot_writer.py

Added a high-level API that generates robot writing commands from strings.

Features:
- Horizontal writing.
- Vertical writing.
- Stroke-order generation using KanjiVG.
- Generation of command sequences for complete strings.

### run_font_bcap_cobotta_writer.py

Added an execution example using COBOTTA b-CAP.

Features:
- Execution of `FontRobotMotionCommand`.
- Fast relative movements using `CobottaBcap.robo_dmove()`.
- Execution of TakeArm / MotorOn / GiveArm.
- Speed, acceleration, and deceleration settings.
- KanjiVG directory configuration.
- Dry Run mode.

---

## v0.0.2 - KanjiVG stroke support

### Added

#### font_stroke_builder.py

Added processing for stroke data with explicit stroke order.

Features:

- Generation of `FontStrokeGlyph`.
- Management of `FontStrokePath`.
- Management of per-stroke data.
- Stroke definitions for alphabetic characters.

#### font_kanjivg_stroke_loader.py

Added processing for loading ordered strokes from KanjiVG SVG files.

Features:

- Loading KanjiVG SVG.
- Parsing SVG paths.
- Transforming SVG coordinates.
- Supporting quadratic Bézier curves.
- Supporting cubic Bézier curves.
- Preserving stroke order.
- Generating `FontStrokeGlyph`.

#### run_font_kanjivg_stroke_test.py

Added a script to inspect KanjiVG stroke rendering.

Features:

- Checking KanjiVG loading.
- Checking stroke rendering.
- Checking stroke order.

#### run_font_kanjivg_motion_test.py

Added a script to inspect motion generation from KanjiVG strokes.

Features:

- Loading KanjiVG.
- Generating motion.
- Visualizing motion.

### Changed

#### font_geometry.py

Added representations for ordered strokes.

Data structures added:

- `FontStrokePath`
- `FontStrokeGlyph`

#### font_motion_builder.py

Added support for motion generation from stroke data as well as centerlines.

Added:

- `build_from_stroke()`

Supported inputs:

```text
FontCenterlineGlyph
FontStrokeGlyph
```

## v0.0.1 - Verified centerline-generation pipeline

### Added

#### font_viewer.py

Added integrated visual inspection of the entire processing pipeline.

Stages that can be inspected:

- `FontOutlineGlyph`
- `FontFilledGlyph`
- `FontCenterlineGlyph`
- Filled + Centerline overlay.

#### font_centerline_cleaner.py

Formally integrated centerline postprocessing into the pipeline.

Features:

- Duplicate-point removal.
- Short-segment removal.
- Point-sequence resampling.
- Uniform point spacing.

#### font_motion_builder.py

Changed the design to accept cleaned centerline data as input.

Features:

- Injection of `FontCenterlineCleaner`.
- Motion generation after centerline cleanup.
- Centerline reconstruction.

### Changed

#### font_outline_extractor.py

Added support for TrueType Collection (TTC) fonts.

Added:

- `font_number` selection.
- Selection of a font within a TTC file.

This enables direct use of standard macOS fonts.

#### font_viewer.py

Changed from testing individual displays to inspecting the complete pipeline.

Before:

```text
Outline
↓
Filled
```

After:

```text
Outline
↓
Filled
↓
Centerline
↓
Filled + Centerline
```

### Verification

Confirmed the following on macOS:

- Loading Hiragino Kaku Gothic TTC.
- Extracting font outlines.
- Generating character regions.
- Skeletonization.
- Extracting centerlines.
- Cleaning centerlines.
- Rendering visualizations.

### Current Processing Flow

```text
FontOutlineExtractor
↓
FontGlyphFiller
↓
FontCenterlineExtractor
↓
FontCenterlineCleaner
↓
FontMotionBuilder
```

### Current Status

In this version, the basic pipeline was confirmed to operate through:

```text
Font
↓
Outline
↓
Fill
↓
Centerline
↓
Motion commands
```

### Current Limitations

- Centerlines are based on skeletonization.
- No stroke-order information is available.
- Stroke structure is not reconstructed.
- Unnatural lines may occur at branches.
- Path connection order optimization is not implemented.
- Pen travel path optimization is not implemented.
- Conversion to robot-specific coordinates is not implemented.
- Z-axis control is not implemented.

### Planned for the Next Version

- Improve `FontMotionBuilder`.
- Optimize path connection order.
- Minimize pen-up travel.
- Improve centerline quality.
- Evaluate quality for Japanese kanji.
- Investigate algorithms for obtaining centerlines directly from outlines.
- Integrate with robot control systems.

## v0.0.0 - Initial prototype

### Added

#### font_geometry.py

Implemented shared data structures for font processing.

Data structures added:

- `FontPoint`
- `FontOutlinePath`
- `FontOutlineGlyph`
- `FontFilledGlyph`
- `FontCenterlinePath`
- `FontCenterlineGlyph`
- `FontMotionCommand`

#### font_outline_extractor.py

Implemented extraction of character outlines from font files.

Features:

- Loading TrueType/OpenType fonts.
- Converting quadratic Bézier curves into point sequences.
- Converting cubic Bézier curves into point sequences.
- Extracting outlines for entire strings.
- Converting font sizes.
- Retrieving glyph outlines.

#### font_fill_glyph.py

Implemented generation of filled character regions from outline data.

Features:

- Point-in-outline testing.
- Binary mask generation.
- Character region generation including internal holes.
- Pixel size configuration.
- Margin configuration.

#### font_centerline_extractor.py

Implemented centerline extraction from filled character regions.

Features:

- Skeletonization.
- Eight-neighbor graph generation.
- Branch-point detection.
- Centerline path extraction.

#### font_centerline_cleaner.py

Implemented cleanup of extracted centerlines for robot use.

Features:

- Duplicate-point removal.
- Short-segment removal.
- Point-sequence resampling.
- Uniform point spacing.

#### font_motion_builder.py

Implemented conversion of centerlines into relative XY motion commands.

Features:

- Pen-up command generation.
- Pen-down command generation.
- Relative XY motion command generation.
- Centerline reconstruction.

#### font_viewer.py

Implemented visualization of intermediate processing data.

Features:

- Outline display.
- Filled-region display.
- Centerline display.
- Filled-region and centerline overlay.

### Processing Flow

The current processing flow is:

```text
FontOutlineExtractor

↓

FontGlyphFiller

↓

FontCenterlineExtractor

↓

FontCenterlineCleaner

↓

FontMotionBuilder
```

### Purpose

Development began as a foundational library for extracting character shapes from standard TrueType/OpenType fonts and converting them into centerline data and motion commands that robots can use to write characters.

### Current Limitations

- Centerline extraction relies on skeletonization after rasterization.
- Stroke order is not reconstructed.
- Calligraphic stroke structure is not reconstructed.
- Centerline quality depends on the font.
- Unnecessary short segments may appear at branch points.
- Segment connection order optimization is not implemented.
- Travel path optimization is not implemented.
- Output in robot-specific formats is not implemented.

### Future Plans

- Improve centerline quality.
- Add branch-removal algorithms.
- Optimize segment connections.
- Optimize travel paths.
- Test multiple fonts.
- Evaluate Japanese character quality.
- Investigate direct centerline extraction from outlines.
- Integrate with robot control libraries.
