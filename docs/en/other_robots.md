# Using Other Robots and Separating the Control Layer

The character and stroke processing in `glyph_motion` is **not specific to COBOTTA**. Generating character geometry and positioned strokes is separate from driving a robot.

## Verified Classes and Responsibilities

- `glyph_motion.lib.font_geometry.FontStrokePath`: represents stroke point sequences.
- `glyph_motion.font_line_layout.FontLineLayout`: loads KanjiVG characters and positions them in character cells; it does not connect to a robot or control pen lifts or motion speeds.
- `glyph_motion.font_line_layout.PositionedCharacter`: stores a character and its positioned `strokes`.
- `glyph_motion.font_bcap_cobotta_writer.FontBcapCobottaWriter`: the COBOTTA-specific control class. It uses `CobottaBcap` and converts handwriting geometry to absolute P-coordinate commands.

## Porting to Another Robot

1. Use `FontLineLayout` to generate positioned strokes from text. Obtain the `strokes` from each returned `PositionedCharacter`.
2. Transform the stroke coordinates into the target robot's coordinate system, units, and writing plane. Define axis signs, XY mapping, origin, tool orientation, and workspace limits for that robot.
3. For each stroke, lift the pen, travel to its first point, lower the pen, and draw the stroke points in order. Lift the pen before traveling to the next stroke.
4. Implement robot-specific connection management, arm acquisition, servo enabling, speed and acceleration settings, stopping, and error recovery in the target robot's controller.
5. Expose that controller through a device server if remote operation is needed. This does **not** mean that `FontBcapCobottaWriter` can control a different robot without adaptation.
6. Before running on hardware, validate generated points, coordinate transformations, workspace boundaries, pen clearance, and emergency-stop behavior.

## COBOTTA and Device Servers

In the supplied implementation, the COBOTTA control front end is **`font_bcap_cobotta_writer.py`**, which defines **`FontBcapCobottaWriter`**. Its implemented methods include `connect()`, `set_params()`, `write()`, and `disconnect()`. The `write(text, start_height_mm=None, return_to_start=None, new_line=None)` method executes handwriting on the robot; it is not a robot-independent API.

The device server's exported method names and client API must be verified separately against the actual server source. Unverified methods such as `write_text()` and `preview_text()` are not presented here as implemented methods of this class.
