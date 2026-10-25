# glyph_motion

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/glyph_motion/blob/main/README.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/glyph_motion/blob/main/README.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fglyph_motion-181717?logo=github)](https://github.com/ohara-lab-su/glyph_motion/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/glpyh_motion/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

`glyph_motion` is a library that converts strokes derived from fonts or KanjiVG, including stroke-order information, into motion commands for robotic handwriting. The commands can be executed through COBOTTA b-CAP or ese774_frame.

## Structure

```text
glyph_motion/
  lib/
    font_*.py
  font_motion_builder.py
  font_robot_motion_builder.py
  font_robot_writer.py
  font_bcap_cobotta_writer.py
  server_fastapi/
    models/
    routers/
    clients/
    spec_writer.py
    server.py
examples/
  run_font_bcap_cobotta_writer_server.py
  client_write_text.py
```

The `lib/` directory is a font-processing layer independent of robotics. It handles TTF/TTC fonts, KanjiVG, outlines, centerlines, and strokes with stroke-order information, without robot-specific processing.

`font_motion_builder.py` converts font-derived strokes or centerlines into robot-independent relative motion commands.

`font_robot_motion_builder.py` and `font_robot_writer.py` convert strings into abstract command sequences for robotic handwriting. They handle pen-up and pen-down actions, writing and travel speeds, and Z-axis lift distances, without depending on COBOTTA-specific APIs.

`font_bcap_cobotta_writer.py` provides a control class that uses `CobottaBcap` to translate abstract handwriting commands into relative P-coordinate motions for execution through COBOTTA b-CAP.

`server_fastapi/` is the server layer that exposes `CobottaBcapFontWriter` through the ese774_frame transparent API.

## COBOTTA b-CAP Handwriting Class

`CobottaBcapFontWriter` is a class library for writing arbitrary strings with COBOTTA b-CAP. It is a control class intended to be called from local applications, servers, or tests, rather than a standalone execution script.

Its main APIs are:

```text
connect()
prepare()
write_text(text, layout=None, execute=True)
preview_text(text, layout=None, max_commands=20)
halt()
reset_error()
disconnect()
get_current_position()
get_config()
set_config(values)
set_text_parameters(...)
set_motion_parameters(...)
set_origin_parameters(...)
set_transform_parameters(...)
```

`write_text()` generates stroke-ordered robot commands from a string. As needed, it establishes a b-CAP connection, performs TakeArm and MotorOn, configures acceleration and deceleration, and prepares the starting pose before executing the commands via `CobottaBcap.robo_dmove(..., coord_mode="P")`.

`preview_text()` returns the number of generated commands and a summary of the initial commands without sending them to the robot.

## Configuration

The primary settings are consolidated in `CobottaBcapFontWriterConfig`.

### Connection Settings

```text
host
port
kanjivg_directory
```

### Text Generation Settings

```text
layout
character_height_mm
character_spacing_mm
pen_lift_height_mm
curve_division
```

`character_height_mm` specifies the height of one character. `curve_division` specifies the number of curve subdivisions: increasing it produces smoother trajectories but also increases the number of commands.

### Motion Settings

```text
drawing_speed
travel_speed
pen_up_speed
pen_down_speed
approach_speed
accel
decel
move_interval_sec
max_travel_step_mm
skip_zero_move
zero_move_epsilon
```

`drawing_speed` controls XY motion while writing, whereas `travel_speed` controls XY motion when not writing. `pen_up_speed` and `pen_down_speed` are used for Z-axis retraction and contact motions. `move_interval_sec` is the delay after issuing each motion command; setting it to 0.0 minimizes the interval between commands. `max_travel_step_mm` is the maximum step size used when subdividing large non-writing XY moves.

If motion is too slow, first adjust `travel_speed`, `drawing_speed`, `accel`, `decel`, `move_interval_sec`, and `curve_division`.

### Origin and Writing Surface Settings

```text
origin_mode
surface_z_mode
robot_origin_x
robot_origin_y
robot_surface_z
approach_lift_height_mm
```

The supported `origin_mode` values are:

```text
current_as_first_stroke
current_as_origin
absolute_origin
```

`current_as_first_stroke` treats the XY coordinates of the current robot position as the starting point of the first stroke. It is the default for physical robot adjustment because it reduces the initial large XY move.

`current_as_origin` treats the XY coordinates of the current position as character coordinates `(0, 0)`.

`absolute_origin` uses `robot_origin_x` and `robot_origin_y` as character coordinates `(0, 0)`.

The supported `surface_z_mode` values are:

```text
current
absolute
```

`current` treats the current Z coordinate as the writing surface. `absolute` uses `robot_surface_z` as the writing surface Z coordinate.

### Coordinate Mapping Settings

```text
robot_x_sign
robot_y_sign
robot_z_sign
robot_x_scale
robot_y_scale
robot_z_scale
robot_drx
robot_dry
robot_drz
```

These settings define axis directions, scale factors, and orientation offsets between character coordinates and COBOTTA P coordinates. Adjust them to match the paper placement, pen orientation, and robot coordinate system.

## Server Integration with ese774_frame

COBOTTA handwriting requires relatively little communication and does not need continuous high-volume transfers such as image streaming. It is therefore exposed through the ese774_frame FastAPI transparent API rather than gRPC.

The exposed object name is:

```text
cobotta_writer
```

The public API is defined in `server_fastapi/spec_writer.py`.

Its main methods are:

```text
connect
prepare
disconnect
close
halt
reset_error
is_connected
get_current_position
get_config
set_config
set_text_parameters
set_motion_parameters
set_origin_parameters
set_transform_parameters
preview_text
write_text
```

A server startup example is provided in `examples/run_font_bcap_cobotta_writer_server.py`. A client example is provided in `examples/client_write_text.py`.

## Operational Notes

Before operating the physical robot, use `preview_text()` to check the number of commands and the initial commands.

For initial calibration, use `origin_mode="current_as_first_stroke"` and `surface_z_mode="current"`. Position the pen tip at the starting point of the first stroke and on the writing surface before execution.

If an out-of-range motion error occurs, check the origin mode, character size, XY axis signs, XY scale factors, and current position.

If writing is too slow, set `move_interval_sec` to 0.0 and increase `travel_speed`, `drawing_speed`, `accel`, and `decel`. If curves are subdivided excessively, reduce `curve_division`.

## Current implementation and use with other robots

**Implementation status.** The COBOTTA-specific source supplied for this revision is `glyph_motion/font_bcap_cobotta_writer.py`. It defines `FontBcapCobottaWriter` and `FontBcapCobottaWriterConfig`. The actual control entry point is `FontBcapCobottaWriter.write(text, start_height_mm=None, return_to_start=None, new_line=None)`. Other implemented methods include `connect()`, `disconnect()`, `set_params()`, `reset_error()`, and `emergency_lift_pen()`. This source does **not** define the `CobottaBcapFontWriter`, `write_text()`, or `preview_text()` API described in the earlier README sections above. Those earlier descriptions are retained for information preservation, not as confirmation that the APIs exist in the supplied implementation.

The library's font geometry and layout components are **not COBOTTA-specific**. `glyph_motion.font_line_layout.FontLineLayout` constructs positioned characters and their stroke paths without connecting to a robot. `glyph_motion.font_line_layout.PositionedCharacter` holds the positioned strokes; `glyph_motion.lib.font_geometry.FontStrokePath` represents a stroke. `FontBcapCobottaWriter` is only the COBOTTA b-CAP execution adapter, not a prerequisite for using the geometry layer.

### Adapting the output to another robot

1. Create the text layout with `FontLineLayout` and obtain the stroke paths from the returned positioned characters.
2. Convert the points into the target robot's units and coordinate frame, including the writing-plane origin, axis orientation, tool orientation, and permitted workspace.
3. Implement pen-up travel to each stroke's first point, pen-down drawing along its ordered points, and pen-up clearance between strokes in the target robot's control class.
4. Implement connection, robot enablement, motion parameters, error handling, and stopping with that robot's own API. Do not reuse COBOTTA b-CAP motion commands on other robot types.
5. If network control is needed, expose **the robot-specific controller** through a device server. The device-server front-end for the supplied COBOTTA implementation is `font_bcap_cobotta_writer.py`; it must not be mistaken for the generic stroke generator. The exact server API needs confirmation against its own source.
6. Validate trajectories, coordinate transformations, workspace limits, pen clearance, and emergency stopping before operating hardware.

The detailed manual under `docs/` is maintained separately from these README files.
