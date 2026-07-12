"""FontBcapCobottaWriter を ese774_frame の動的 FastAPI 経路へ公開する API spec。"""

from ese774_frame.models.api_spec import ApiSpec

from glyph_motion.server_fastapi.models.common import ResultResponse
from glyph_motion.server_fastapi.models.writer import (
    SetParamsRequest,
    WriteRequest,
)


cobotta_writer_api_spec = [
    ApiSpec(
        name="connect",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="b-CAP サーバーへ接続する",
        summary="Connect",
    ),
    ApiSpec(
        name="disconnect",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="b-CAP 接続を切断する",
        summary="Disconnect",
    ),
    ApiSpec(
        name="reset_error",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="コントローラのエラーを解除する",
        summary="Reset error",
    ),
    ApiSpec(
        name="take_arm",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="アーム権限を取得する",
        summary="Take arm",
    ),
    ApiSpec(
        name="give_arm",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="アーム権限を返却する",
        summary="Give arm",
    ),
    ApiSpec(
        name="motor_on",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="モータを投入する",
        summary="Motor ON",
    ),
    ApiSpec(
        name="set_accel",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="設定済みの加速度をロボットへ反映する",
        summary="Set accel",
    ),
    ApiSpec(
        name="set_decel",
        object_name="cobotta_writer",
        request_model=None,
        response_model=ResultResponse,
        method="post",
        description="設定済みの減速度をロボットへ反映する",
        summary="Set decel",
    ),
    ApiSpec(
        name="set_params",
        object_name="cobotta_writer",
        request_model=SetParamsRequest,
        response_model=ResultResponse,
        method="post",
        description="通信設定以外の書字設定を更新する",
        summary="Set parameters",
    ),
    ApiSpec(
        name="write",
        object_name="cobotta_writer",
        request_model=WriteRequest,
        response_model=ResultResponse,
        method="post",
        description="固定作業空間へ一行の文字列を書字する",
        summary="Write text",
    ),
]
