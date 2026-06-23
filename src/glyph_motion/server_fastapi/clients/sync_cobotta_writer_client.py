"""COBOTTA 文字書字 ese774_frame 同期クライアント。"""

import asyncio
from typing import Any, Optional

from .async_cobotta_writer_client import AsyncCobottaWriterClient
from ..spec_writer import cobotta_writer_api_spec


class SyncCobottaWriterClient(AsyncCobottaWriterClient):
    """AsyncCobottaWriterClient の同期ラッパーである。"""

    def __init__(
        self,
        config: Optional[Any] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        logger: Optional[Any] = None,
        log_level: str = "INFO",
        timeout_sec: float = 120.0,
    ) -> None:
        super().__init__(
            config=config,
            server_ip=server_ip,
            server_port=server_port,
            logger=logger,
            log_level=log_level,
            timeout_sec=timeout_sec,
        )
        self._register_sync_methods()

    @staticmethod
    def _sync_wrap(coro):
        try:
            return asyncio.run(coro)
        except RuntimeError:
            import nest_asyncio

            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)

    def _register_sync_methods(self) -> None:
        for api in cobotta_writer_api_spec:
            async_method = getattr(self, api.name)

            def make_sync_method(method):
                def sync_method(*args, **kwargs):
                    return self._sync_wrap(method(*args, **kwargs))

                sync_method.__name__ = method.__name__
                return sync_method

            object.__setattr__(self, api.name, make_sync_method(async_method))

    def dispatch(self, method: str, *args, **kwargs):
        return self._sync_wrap(super().dispatch(method, *args, **kwargs))

    def close_client(self) -> None:
        self._sync_wrap(super().close())
