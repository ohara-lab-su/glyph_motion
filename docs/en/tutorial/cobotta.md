# Writing with COBOTTA

`FontBcapCobottaWriter` converts positioned strokes derived from KanjiVG into absolute COBOTTA P coordinates and writes them using b-CAP.

## Basic example

```python
from pathlib import Path

from glyph_motion.lib.font_bcap_cobotta_writer import (
    FontBcapCobottaWriter,
    FontBcapCobottaWriterConfig,
)

config = FontBcapCobottaWriterConfig(
    kanjivg_directory=Path("kanjivg/kanji"),
    host="10.170.10.53",
    port=5007,
    workspace_width=200.0,
    workspace_height=100.0,
    cell_width=8.0,
    cell_height=8.0,
    character_height=7.0,
    curve_division=16,
    pen_lift_mm=1.0,
    robot_x_sign=1.0,
    robot_y_sign=1.0,
    robot_swap_xy=False,
    writing_direction="horizontal",
    line_direction="left_to_right",
    drawing_speed=35,
    travel_speed=40,
    pen_speed=20,
    accel=100,
    decel=100,
)

writer = FontBcapCobottaWriter(config=config)

try:
    if not writer.connect():
        raise RuntimeError("Cannot connect to COBOTTA.")
    if not writer.reset_error():
        raise RuntimeError("Failed to reset errors.")
    if not writer.take_arm():
        raise RuntimeError("Failed to acquire arm control.")
    if not writer.motor_on():
        raise RuntimeError("Failed to turn on the motors.")
    if not writer.set_accel():
        raise RuntimeError("Failed to set acceleration.")
    if not writer.set_decel():
        raise RuntimeError("Failed to set deceleration.")

    if not writer.write(
        text="島根大学",
        start_height_mm=1.0,
        return_to_start=True,
    ):
        raise RuntimeError("Writing failed.")
finally:
    writer.emergency_lift_pen()
    writer.give_arm()
    writer.disconnect()
```

## Determining the writing surface

The writing surface is the current Z coordinate at the time of the `write()` call minus `start_height_mm`.

```text
surface_z = start_pose_z - start_height_mm
pen_up_z  = surface_z + pen_lift_mm
```

If the initial pose is on the writing surface (`start_height_mm == 0.0`), the pen is raised in place before moving to the first stroke's start point. If the initial pose is already above the writing surface, the robot maintains that height while moving to the first start point.

## Absolute coordinate transformation

The initial pose of the first `write()` call is saved as the origin for the entire document. Character coordinates are optionally swapped in XY, multiplied by each axis sign, and added to the origin. Orientation components remain those of the initial pose.

## Continuing writing and line breaks

Calling `write()` multiple times on the same writer preserves the logical cursor so that subsequent calls continue where the previous call ended.

```python
writer.write("島根", return_to_start=True)
writer.write("大学", return_to_start=True, new_line=False)
writer.write("材料", return_to_start=True, new_line=True)
```

`return_to_start` controls only whether the robot physically returns to the pose at the beginning of that call. The logical writing position for the next call is preserved.

For horizontal writing, the line-break direction is specified by `horizontal_new_line_direction`. For vertical writing, the column-break direction is specified by `vertical_new_line_direction`. If omitted, these directions are determined automatically from the axis-inversion settings.

## Retraction on failure

`emergency_lift_pen()` moves synchronously to the planned pen-up Z height retained during writing. If the current position is already higher, it maintains the current Z height rather than lowering the pen.
