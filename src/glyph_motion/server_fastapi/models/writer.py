"""COBOTTA 文字書字 API 用 Pydantic モデルである。"""

from typing import Optional

from pydantic import BaseModel


class WriteRequest(BaseModel):
    """一行書字リクエスト。"""

    text: str
    start_height_mm: Optional[float] = None
    return_to_start: Optional[bool] = None
    new_line: Optional[bool] = None


class SetStartHeightMmRequest(BaseModel):
    """既定の書字開始高さ設定リクエスト。"""

    start_height_mm: float


class SetPenLiftMmRequest(BaseModel):
    """ペン退避高さ設定リクエスト。"""

    pen_lift_mm: float


class SetReturnToStartRequest(BaseModel):
    """既定の原点復帰設定リクエスト。"""

    return_to_start: bool


class SetNewLineRequest(BaseModel):
    """既定の改行設定リクエスト。"""

    new_line: bool


class SetParamsRequest(BaseModel):
    """通信設定以外の書字設定更新リクエスト。"""

    kanjivg_directory: Optional[str] = None
    workspace_width: Optional[float] = None
    workspace_height: Optional[float] = None
    cell_width: Optional[float] = None
    cell_height: Optional[float] = None
    character_height: Optional[float] = None
    curve_division: Optional[int] = None
    start_height_mm: Optional[float] = None
    pen_lift_mm: Optional[float] = None
    return_to_start: Optional[bool] = None
    new_line: Optional[bool] = None
    robot_x_sign: Optional[float] = None
    robot_y_sign: Optional[float] = None
    robot_swap_xy: Optional[bool] = None
    line_direction: Optional[str] = None
    writing_direction: Optional[str] = None
    vertical_direction: Optional[str] = None
    horizontal_new_line_direction: Optional[str] = None
    vertical_new_line_direction: Optional[str] = None
    mirror_horizontal: Optional[bool] = None
    mirror_vertical: Optional[bool] = None
    drawing_speed: Optional[int] = None
    travel_speed: Optional[int] = None
    pen_speed: Optional[int] = None
    accel: Optional[int] = None
    decel: Optional[int] = None
