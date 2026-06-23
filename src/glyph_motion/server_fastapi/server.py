"""COBOTTA 文字書字 FastAPI サーバー構築用の薄い起動層。"""

from typing import Any, Dict, Optional

from ese774_frame.api_server import FastApiServer

from glyph_motion.font_bcap_cobotta_writer import CobottaBcapFontWriter
from glyph_motion.font_bcap_cobotta_writer import CobottaBcapFontWriterConfig

from .routers.font_bcap_cobotta_writer_router import FontBcapCobottaWriterRouter
from .spec_writer import cobotta_writer_api_spec


def create_server(
    config: Optional[Any] = None,
    *,
    writer_config: Optional[CobottaBcapFontWriterConfig] = None,
    device_kwargs: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
    log_level: str = "INFO",
) -> FastApiServer:
    """CobottaBcapFontWriter 用 FastApiServer を作成する。"""
    kwargs = dict(device_kwargs or {})
    kwargs.setdefault("config", writer_config or CobottaBcapFontWriterConfig())
    return FastApiServer(
        device_cls=CobottaBcapFontWriter,
        router_cls=FontBcapCobottaWriterRouter,
        config=config,
        api_spec=cobotta_writer_api_spec,
        device_kwargs=kwargs,
        logger=logger,
        log_level=log_level,
        lifespan_msg_prefix="CobottaWriter",
    )


def run(
    config: Optional[Any] = None,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    writer_config: Optional[CobottaBcapFontWriterConfig] = None,
    device_kwargs: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
    log_level: str = "INFO",
) -> None:
    """COBOTTA 文字書字 FastAPI サーバーを起動する。"""
    create_server(
        config=config,
        writer_config=writer_config,
        device_kwargs=device_kwargs,
        logger=logger,
        log_level=log_level,
    ).run(host=host, port=port, reload=reload)
