"""CobottaFontLineWriter ese774_frame 非同期クライアント。"""

from typing import Any, Optional

from ese774_frame.clients.async_device_client import AsyncDeviceClient

from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec


class AsyncCobottaWriterClient(AsyncDeviceClient):
    """CobottaFontLineWriter を ese774_frame 経由で呼ぶ非同期クライアント。"""

    def __init__(
        self,
        config: Optional[Any] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        logger: Optional[Any] = None,
        log_level: str = "INFO",
        timeout_sec: float = 120.0,
    ) -> None:
        if config is not None:
            server_ip = getattr(config, "SERVER_IP", server_ip)
            server_port = getattr(config, "SERVER_PORT", server_port)

        if server_ip is None:
            server_ip = "127.0.0.1"

        if server_port is None:
            server_port = 8000

        super().__init__(
            server_ip=server_ip,
            server_port=int(server_port),
            base_url="http://{}:{}".format(server_ip, server_port),
            api_spec=cobotta_writer_api_spec,
            logger=logger,
            log_level=log_level,
            object_name="cobotta_writer",
            timeout_sec=timeout_sec,
        )
