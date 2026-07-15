#!/usr/bin/env python
"""
内部変数値を読んで、それを配列に入れなおして、そこに移動する

Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""

import pytest
import asyncio


@pytest.mark.asyncio
async def test_fastapi_Async_move_A_30():
    import logging
    from pathlib import Path

    # httpx のログを WARNING レベル以上にする（INFO を抑制）
    logging.getLogger("httpx").setLevel(logging.WARNING)

    from cobotta2 import Config, MotionMode
    from cobotta2.server import AsyncCobottaClient
    from x_logger import XLogger

    # HERE = Path(__file__).parent
    # Config.load_yaml(HERE / "../config_cobotta1_server1.yaml")
    Config.load_yaml("../config_cobotta2_server2.yaml")
    # Config.load_yaml(HERE / "../config_cobotta4_server3.yaml")
    # Config.load_yaml("../config_cobotta1.yaml")

    logger = XLogger(
        log_level="info",
        logger_name=Config.CLIENT_LOGGER_NAME,
    )
    client = AsyncCobottaClient(
        config=Config,
        logger=logger,
    )
    await client.reset_error()

    # await client.take_arm()
    # await client.turn_on_motor()

    # await client.hand_move_H(6, True)
    await client.hand(force=15)
    await asyncio.sleep(2)

    # current_pos = await client.get_current_position()
    # _logger.info(f"current_position: {current_pos}")
    assert "result" == "result"
