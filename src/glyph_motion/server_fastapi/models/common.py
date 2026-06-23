"""glyph_motion の ese774_frame 共通モデルである。"""

from typing import Any, Optional

from pydantic import BaseModel


class ResultResponse(BaseModel):
    """ese774_frame の標準応答モデルである。"""

    result: Optional[Any] = None


class EmptyRequest(BaseModel):
    """空リクエストである。"""

    pass
