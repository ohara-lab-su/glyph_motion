"""COBOTTA 文字書字 ese774_frame 非同期クライアント。"""

import logging
from typing import Any, Optional

from ese774_frame.clients.async_device_client import AsyncDeviceClient

from ..spec_writer import cobotta_writer_api_spec


class AsyncCobottaWriterClient(AsyncDeviceClient):
    """CobottaBcapFontWriter を ese774_frame 経由で呼ぶ非同期クライアントである。"""

    def __init__(
        self,
        config: Optional[Any] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        logger: Optional[Any] = None,
        log_level: str = "INFO",
        timeout_sec: float = 120.0,
    ) -> None:
        if logger is None:
            logging.basicConfig(level=log_level.upper())
            logger = logging.getLogger(__name__)

        if config is not None:
            server_ip = getattr(config, "SERVER_IP", server_ip)
            server_port = getattr(config, "SERVER_PORT", server_port)

        server_ip = server_ip or "127.0.0.1"
        server_port = int(server_port or 8000)

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            base_url="http://{}:{}".format(server_ip, server_port),
            api_spec=cobotta_writer_api_spec,
            logger=logger,
            log_level=log_level,
            object_name="cobotta_writer",
            timeout_sec=timeout_sec,
        )
