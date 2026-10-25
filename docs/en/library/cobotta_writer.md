# COBOTTA Writing API

## FontBcapCobottaWriterConfig

Holds the communication destination, workspace, character cells, coordinate transforms, writing directions, axis inversions, speeds, and acceleration/deceleration settings.

The main defaults are:

| Argument | Default |
|---|---:|
| `host` | `10.170.10.53` |
| `port` | `5007` |
| `workspace_width` | `200.0` |
| `workspace_height` | `10.0` |
| `cell_width` | `8.0` |
| `cell_height` | `8.0` |
| `character_height` | `7.0` |
| `curve_division` | `16` |
| `pen_lift_mm` | `1.0` |
| `writing_direction` | `horizontal` |
| `line_direction` | `left_to_right` |
| `vertical_direction` | `top_to_bottom` |
| `drawing_speed` | `35` |
| `travel_speed` | `40` |
| `pen_speed` | `20` |
| `accel` / `decel` | `100` |

## FontBcapCobottaWriter

```python
FontBcapCobottaWriter(config, bcap=None, logger=None)
```

If an existing `CobottaBcap` instance is supplied, the writer uses it. Otherwise, the writer creates an instance for the connection.

### Connection and preparation

- `connect() -> bool`
- `disconnect() -> bool`
- `reset_error() -> bool`
- `take_arm() -> bool`
- `give_arm() -> bool`
- `motor_on() -> bool`
- `set_accel() -> bool`
- `set_decel() -> bool`

### Configuration

- `set_params(...) -> bool`
- `set_pen_lift_mm(pen_lift_mm: float) -> bool`
- `set_start_height_mm(start_height_mm: float) -> bool`
- `set_return_to_start(return_to_start: bool) -> bool`
- `set_new_line(new_line: bool) -> bool`

`set_params()` first constructs a new `FontLineLayout` from the proposed layout-related settings and applies the settings only after construction succeeds. This avoids partial updates when an intermediate step fails.

### Writing

```python
write(
    text: str,
    start_height_mm: float | None = None,
    return_to_start: bool | None = None,
    new_line: bool | None = None,
) -> bool
```

Returns `False` when not connected. If the stroke set is empty, it performs no motion and returns `True`. A `RuntimeError` is raised if the current P coordinates cannot be obtained or do not contain six elements.

### Emergency retraction

- `emergency_lift_pen() -> bool`

During writing, retracts along the Z axis to the configured pen-up height while maintaining the current XY coordinates and orientation.
