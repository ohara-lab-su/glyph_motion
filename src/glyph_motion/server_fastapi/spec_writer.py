"""FontBcapCobottaWriter を ese774_frame の動的 FastAPI 経路へ公開する API spec。"""

from ese774_frame.models.api_spec import ApiSpec

from glyph_motion.server_fastapi.models.common import ResultResponse
from glyph_motion.server_fastapi.models.writer import SetParamsRequest
from glyph_motion.server_fastapi.models.writer import WriteRequest


OBJECT_NAME = "cobotta_writer"


def _api(name, request_model=None, summary=""):
    return ApiSpec(
        name=name,
        object_name=OBJECT_NAME,
        request_model=request_model,
        response_model=ResultResponse,
        method="post",
        summary=summary or name,
    )


cobotta_writer_api_spec = [
    _api("connect", summary="b-CAP に接続する"),
    _api("prepare", summary="TakeArm、MotorOn、加減速設定を行う"),
    _api(
        "set_params",
        SetParamsRequest,
        summary="通信設定以外の書字設定を更新する",
    ),
    _api("close", summary="GiveArm と b-CAP 切断を行う"),
    _api("write", WriteRequest, summary="固定作業空間へ一行の文字列を書く"),
]
