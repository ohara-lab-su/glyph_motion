# COBOTTA書字 API

## FontBcapCobottaWriterConfig

通信先、作業空間、文字セル、座標変換、書字方向、反転、速度、加減速を保持します。

主な既定値は次のとおりです。

| 引数 | 既定値 |
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

既存の `CobottaBcap` を渡した場合は、そのインスタンスを利用します。省略時はwriterが接続用インスタンスを生成します。

### 接続・準備

- `connect() -> bool`
- `disconnect() -> bool`
- `reset_error() -> bool`
- `take_arm() -> bool`
- `give_arm() -> bool`
- `motor_on() -> bool`
- `set_accel() -> bool`
- `set_decel() -> bool`

### 設定

- `set_params(...) -> bool`
- `set_pen_lift_mm(pen_lift_mm: float) -> bool`
- `set_start_height_mm(start_height_mm: float) -> bool`
- `set_return_to_start(return_to_start: bool) -> bool`
- `set_new_line(new_line: bool) -> bool`

`set_params()` は、レイアウトに関係する新設定から先に新しい `FontLineLayout` を構築し、成功後に設定へ反映します。途中失敗による部分更新を避ける構造です。

### 書字

```python
write(
    text: str,
    start_height_mm: float | None = None,
    return_to_start: bool | None = None,
    new_line: bool | None = None,
) -> bool
```

接続されていない場合は `False` を返します。ストロークが空の場合は動作せず `True` を返します。現在P座標を取得できない場合や6要素でない場合は `RuntimeError` です。

### 緊急退避

- `emergency_lift_pen() -> bool`

書字途中に設定されたペン上げ高さを使用して、現在XYと姿勢を維持したままZ方向へ退避します。
