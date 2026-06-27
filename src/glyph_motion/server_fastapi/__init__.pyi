from typing import Any, Literal, Optional, overload

from glyph_motion.server_fastapi.clients.async_cobotta_writer_client import AsyncCobottaWriterClient
from glyph_motion.server_fastapi.clients.sync_cobotta_writer_client import SyncCobottaWriterClient
from glyph_motion.server_fastapi.routers.font_bcap_cobotta_writer_router import FontBcapCobottaWriterRouter
from glyph_motion.server_fastapi.server import create_server, run
from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec

@overload
def DeviceProxy(
    device_class: Literal["cobotta_writer"],
    *args: Any,
    async_mode: Literal[False] = False,
    **kwargs: Any,
) -> SyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["cobotta_writer"],
    *args: Any,
    async_mode: Literal[True],
    **kwargs: Any,
) -> AsyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["CobottaWriter"],
    *args: Any,
    async_mode: Literal[False] = False,
    **kwargs: Any,
) -> SyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["CobottaWriter"],
    *args: Any,
    async_mode: Literal[True],
    **kwargs: Any,
) -> AsyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["FontBcapCobottaWriter"],
    *args: Any,
    async_mode: Literal[False] = False,
    **kwargs: Any,
) -> SyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["FontBcapCobottaWriter"],
    *args: Any,
    async_mode: Literal[True],
    **kwargs: Any,
) -> AsyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["font_bcap_cobotta_writer"],
    *args: Any,
    async_mode: Literal[False] = False,
    **kwargs: Any,
) -> SyncCobottaWriterClient: ...

@overload
def DeviceProxy(
    device_class: Literal["font_bcap_cobotta_writer"],
    *args: Any,
    async_mode: Literal[True],
    **kwargs: Any,
) -> AsyncCobottaWriterClient: ...

def DeviceProxy(
    device_class: str,
    *args: Any,
    async_mode: Optional[bool] = None,
    **kwargs: Any,
) -> Any: ...

__all__ = [
    "DeviceProxy",
    "AsyncCobottaWriterClient",
    "SyncCobottaWriterClient",
    "FontBcapCobottaWriterRouter",
    "cobotta_writer_api_spec",
    "create_server",
    "run",
]
