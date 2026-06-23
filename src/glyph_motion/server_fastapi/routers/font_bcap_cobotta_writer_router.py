"""CobottaBcapFontWriter と api_spec を結ぶ ese774_frame Router。"""

from typing import Any, Optional

from ese774_frame.routers.device_router import DeviceRouter


class FontBcapCobottaWriterRouter(DeviceRouter):
    """DeviceRouter の動的ディスパッチをそのまま使用する薄い Router である。"""

    def __init__(
        self,
        device_instance: Any,
        api_spec=None,
        logger: Optional[Any] = None,
        log_level: str = "INFO",
    ) -> None:
        super().__init__(
            device_instance,
            api_spec=api_spec,
            logger=logger,
            log_level=log_level,
        )
