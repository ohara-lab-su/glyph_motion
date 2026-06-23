"""COBOTTA 文字書字 API 用 Pydantic モデルである。"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class WriteTextRequest(BaseModel):
    text: str
    layout: Optional[str] = None
    execute: bool = True


class PreviewTextRequest(BaseModel):
    text: str
    layout: Optional[str] = None
    max_commands: int = 20


class SetConfigRequest(BaseModel):
    values: Dict[str, Any]


class TextParametersRequest(BaseModel):
    character_height_mm: Optional[float] = None
    character_spacing_mm: Optional[float] = None
    pen_lift_height_mm: Optional[float] = None
    curve_division: Optional[int] = None
    layout: Optional[str] = None


class MotionParametersRequest(BaseModel):
    drawing_speed: Optional[int] = None
    travel_speed: Optional[int] = None
    pen_up_speed: Optional[int] = None
    pen_down_speed: Optional[int] = None
    approach_speed: Optional[int] = None
    accel: Optional[float] = None
    decel: Optional[float] = None
    move_interval_sec: Optional[float] = None
    max_travel_step_mm: Optional[float] = None
    curve_division: Optional[int] = None


class OriginParametersRequest(BaseModel):
    origin_mode: Optional[str] = None
    surface_z_mode: Optional[str] = None
    robot_origin_x: Optional[float] = None
    robot_origin_y: Optional[float] = None
    robot_surface_z: Optional[float] = None
    approach_lift_height_mm: Optional[float] = None


class TransformParametersRequest(BaseModel):
    robot_x_sign: Optional[float] = None
    robot_y_sign: Optional[float] = None
    robot_z_sign: Optional[float] = None
    robot_x_scale: Optional[float] = None
    robot_y_scale: Optional[float] = None
    robot_z_scale: Optional[float] = None
    robot_drx: Optional[float] = None
    robot_dry: Optional[float] = None
    robot_drz: Optional[float] = None
