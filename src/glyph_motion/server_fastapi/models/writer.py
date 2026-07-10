"""CobottaFontLineWriter API 用 Pydantic モデル。"""

from pydantic import BaseModel


class WriteRequest(BaseModel):
    """一行書字リクエスト。"""

    text: str
    start_height_mm: float = 0.0
    return_to_start: bool = True
