"""COBOTTA 文字書字 API 用 Pydantic モデルである。"""

from typing import Optional

from pydantic import BaseModel


class WriteRequest(BaseModel):
    """一行書字リクエスト。"""

    text: str
    start_height_mm: float = 0.0
    return_to_start: bool = True


class SetParamsRequest(BaseModel):
    """通信設定以外の書字設定更新リクエスト。"""

    kanjivg_directory: Optional[str] = None
    workspace_width: Optional[float] = None
    workspace_height: Optional[float] = None
    cell_width: Optional[float] = None
    cell_height: Optional[float] = None
    character_height: Optional[float] = None
    curve_division: Optional[int] = None
    pen_lift_mm: Optional[float] = None
    robot_x_sign: Optional[float] = None
    robot_y_sign: Optional[float] = None
    robot_swap_xy: Optional[bool] = None
    line_direction: Optional[str] = None
    writing_direction: Optional[str] = None
    vertical_direction: Optional[str] = None
    mirror_horizontal: Optional[bool] = None
    mirror_vertical: Optional[bool] = None
    drawing_speed: Optional[int] = None
    travel_speed: Optional[int] = None
    pen_speed: Optional[int] = None
    accel: Optional[int] = None
    decel: Optional[int] = None
