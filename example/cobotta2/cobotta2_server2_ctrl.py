#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com

start ORiN2 cobotta2 server
"""

from cobotta2 import Config, CobottaCtrl

# from cobotta2.server import CobottaRouterCtrl, cobotta_ctrl_api_spec
from cobotta2.server_fastapi import CobottaRouterCtrl
from cobotta2.server_fastapi import cobotta_ctrl_api_spec

# from cobotta2.config import Config
# from cobotta2.cobotta_ctrl import CobottaCtrl
# from cobotta2.server_fastapi import CobottaRouterCtrl
# from cobotta2.server_fastapi import cobotta_ctrl_api_spec

from ese774_frame import FastApiServer

# from ese774_frame.api_server import FastApiServer
from x_logger import XLogger

if __name__ == "__main__":
    ##########
    Config.load_yaml("../config_cobotta2_server2.yaml")
    ##########

    logger = XLogger(
        log_level="debug",
        logger_name=Config.SERVER_LOGGER_NAME,
        log_mode="rotate",
        # log_mode="file",
        log_name=f"c:/opt/log/{Config.SERVER_LOGGER_NAME}.log",
    )

    logger.info(f"COBOTTA IP = {Config.COBOTTA_IP}")
    logger.info(f"SERVER IP = {Config.SERVER_IP}")
    logger.info(f"SERVER PORT = {Config.SERVER_PORT}")

    server = FastApiServer(
        device_cls=CobottaCtrl,  # 制御クラス
        # device_cls=CobottaOrin2,  # 制御クラス
        router_cls=CobottaRouterCtrl,  # routerクラス
        config=Config,
        api_spec=cobotta_ctrl_api_spec,
        device_kwargs={
            "cobotta_ip": Config.COBOTTA_IP,
            # "backend": "bcap",
            "backend": "orin2",
        },  # COBOTTA制御Classのコンストラクタ引数)
        logger=logger,
        logger_name=Config.SERVER_LOGGER_NAME,  # LOGGER_NAME
        lifespan_msg_prefix="COBOTTA",
    )
    server.run(
        host=Config.SERVER_IP,
        port=Config.SERVER_PORT,
    )
