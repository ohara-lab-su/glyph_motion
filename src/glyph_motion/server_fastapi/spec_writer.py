"""CobottaBcapFontWriter を ese774_frame の動的 FastAPI 経路へ公開する API spec。"""

from ese774_frame.models.api_spec import ApiSpec

from .models.common import ResultResponse
from .models.writer import (
    MotionParametersRequest,
    OriginParametersRequest,
    PreviewTextRequest,
    SetConfigRequest,
    TextParametersRequest,
    TransformParametersRequest,
    WriteTextRequest,
)


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
    _api("prepare", summary="TakeArm、MotorOn、加減速設定、開始姿勢準備を行う"),
    _api("disconnect", summary="b-CAP 接続を閉じる"),
    _api("close", summary="終了処理を行う"),
    _api("halt", summary="ロボット動作を停止する"),
    _api("reset_error", summary="COBOTTA エラーをリセットする"),
    _api("is_connected", summary="接続状態を返す"),
    _api("get_current_position", summary="現在 P 座標を取得する"),
    _api("get_config", summary="現在設定を返す"),
    _api("set_config", SetConfigRequest, summary="設定値をまとめて更新する"),
    _api("set_text_parameters", TextParametersRequest, summary="文字生成条件を更新する"),
    _api("set_motion_parameters", MotionParametersRequest, summary="速度・加減速・投入間隔を更新する"),
    _api("set_origin_parameters", OriginParametersRequest, summary="書字原点と書字面 Z を更新する"),
    _api("set_transform_parameters", TransformParametersRequest, summary="ロボット座標写像を更新する"),
    _api("preview_text", PreviewTextRequest, summary="ロボットへ投入せず命令概要を返す"),
    _api("write_text", WriteTextRequest, summary="任意文字列を書く"),
]
