"""FontBcapCobottaWriter FastAPI サーバー構築用の起動層。"""

from typing import Any, Dict, Optional

from ese774_frame.api_server import FastApiServer

from glyph_motion.font_bcap_cobotta_writer import FontBcapCobottaWriter
from glyph_motion.font_bcap_cobotta_writer import FontBcapCobottaWriterConfig
from glyph_motion.server_fastapi.routers.font_bcap_cobotta_writer_router import (
    FontBcapCobottaWriterRouter,
)
from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec


def create_server(
    config: Optional[Any] = None,
    *,
    writer_config: Optional[FontBcapCobottaWriterConfig] = None,
    device_kwargs: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
    log_level: str = "INFO",
) -> FastApiServer:
    """FontBcapCobottaWriter 用 FastApiServer を作成する。

    FontBcapCobottaWriterConfig は kanjivg_directory を必須とするため、
    writer_config または device_kwargs["config"] のどちらかを必ず渡す。
    """
    kwargs = dict(device_kwargs or {})

    if writer_config is not None:
        kwargs.setdefault("config", writer_config)

    if "config" not in kwargs:
        raise ValueError(
            "writer_config または device_kwargs['config'] に "
            "FontBcapCobottaWriterConfig を指定してください。"
        )

    return FastApiServer(
        device_cls=FontBcapCobottaWriter,
        router_cls=FontBcapCobottaWriterRouter,
        config=config,
        api_spec=cobotta_writer_api_spec,
        device_kwargs=kwargs,
        logger=logger,
        log_level=log_level,
        lifespan_msg_prefix="CobottaLineWriter",
    )


def run(
    config: Optional[Any] = None,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    writer_config: Optional[FontBcapCobottaWriterConfig] = None,
    device_kwargs: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
    log_level: str = "INFO",
) -> None:
    """FontBcapCobottaWriter FastAPI サーバーを起動する。"""
    server = create_server(
        config=config,
        writer_config=writer_config,
        device_kwargs=device_kwargs,
        logger=logger,
        log_level=log_level,
    )
    server.run(
        host=host,
        port=port,
        reload=reload,
    )
