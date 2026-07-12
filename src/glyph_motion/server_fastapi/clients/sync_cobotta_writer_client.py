"""CobottaFontLineWriter ese774_frame 同期クライアント。"""

from typing import Any

from ese774_frame.clients.sync_device_client import SyncDeviceClient

from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec


class SyncCobottaWriterClient(
    SyncDeviceClient,
):
    """CobottaFontLineWriter を ese774_frame 経由で呼ぶ同期クライアント。"""

    def __init__(
        self,
        config=None,
        server_ip: str = None,
        server_port: int = None,
        logger: Any = None,
        log_level: str = "INFO",
    ):
        if logger is None:
            import logging

            logging.basicConfig(level="INFO")
            logger = logging.getLogger(__name__)

        self._logger = logger

        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.SERVER_PORT

        base_url = "http://{}:{}".format(
            server_ip,
            server_port,
        )
        self._base_url = base_url

        self._logger.info("[CLIENT] server_ip = %s", server_ip)
        self._logger.info("[CLIENT] server_port = %s", server_port)
        self._logger.info("[CLIENT] base_url = %s", base_url)

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            api_spec=cobotta_writer_api_spec,
            base_url=base_url,
            logger=logger,
        )
