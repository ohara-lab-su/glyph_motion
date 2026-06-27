#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
glyph_motion.server_fastapi の pyi 生成用 make.py である。

このスクリプトは ese774_frame 側の pyi 生成器を使い、次の stub を生成する。

・ clients/async_cobotta_writer_client.pyi
・ clients/sync_cobotta_writer_client.pyi
・ clients/__init__.pyi
・ routers/font_bcap_cobotta_writer_router.pyi
・ __init__.pyi

目的は、実装側の薄い client / router を API spec から型補完可能にし、
DeviceProxy("cobotta_writer") の戻り型も __init__.pyi に反映することである。
制御クラス CobottaBcapFontWriter 本体や glyph_motion の通常 API はここでは生成対象にしない。
"""

import os
import re
from contextlib import contextmanager

from ese774_frame.clients.make_pyi_device_client import make_pyi_device_client
from ese774_frame.clients.make_pyi_device_proxy import make_pyi_device_proxy
from ese774_frame.routers.make_pyi_device_router import make_pyi_device_router

from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec


CLIENT_DIR = "clients"
ROUTER_DIR = "routers"

ASYNC_CLIENT_PYI = "async_cobotta_writer_client.pyi"
SYNC_CLIENT_PYI = "sync_cobotta_writer_client.pyi"
CLIENT_INIT_PYI = "__init__.pyi"
ROUTER_PYI = "font_bcap_cobotta_writer_router.pyi"
SERVER_INIT_PYI = "__init__.pyi"

ASYNC_CLIENT_CLASS = "AsyncCobottaWriterClient"
SYNC_CLIENT_CLASS = "SyncCobottaWriterClient"
ROUTER_CLASS = "FontBcapCobottaWriterRouter"

DEVICE_CLASS = "cobotta_writer"
DEVICE_ALIASES = [
    "CobottaWriter",
    "FontBcapCobottaWriter",
    "font_bcap_cobotta_writer",
]


@contextmanager
def chdir(path):
    prev_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)


def _read_lines(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def _write_lines(filename, lines):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _ensure_import(lines, import_line):
    """import_line を最初の class 定義より前に一度だけ挿入する。"""
    if any(line.strip() == import_line.strip() for line in lines):
        return lines

    out = []
    inserted = False
    for line in lines:
        if not inserted and line.startswith("class "):
            out.append(import_line)
            inserted = True
        out.append(line)

    if not inserted:
        out.append(import_line)

    return out


def _replace_class_base(lines, class_name, base_class_name):
    """生成 pyi の class 定義を実装側の継承関係に合わせる。"""
    pattern = re.compile(
        r"^(class\s+" + re.escape(class_name) + r")\s*(?:\([^)]*\))?:\s*$"
    )
    target = "class {}({}):".format(class_name, base_class_name)

    out = []
    for line in lines:
        if pattern.match(line):
            out.append(target)
        else:
            out.append(line)
    return out


def _find_class_block(lines, class_name):
    pattern = re.compile(r"^class\s+" + re.escape(class_name) + r"(?:\(|:)")
    start = None

    for index, line in enumerate(lines):
        if pattern.match(line):
            start = index
            break

    if start is None:
        raise RuntimeError("class not found in generated pyi: {}".format(class_name))

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "\t", "#")):
            end = index
            break

    return start, end


def _member_signature_key(line):
    stripped = line.strip()
    if stripped.startswith("async def "):
        return stripped.split("(", 1)[0]
    if stripped.startswith("def "):
        return stripped.split("(", 1)[0]
    if stripped.startswith("@"):
        return stripped
    return stripped


def _ensure_class_members(lines, class_name, member_lines):
    """API spec 外で .py 側に存在するメソッドを class ブロック内に追加する。"""
    if not member_lines:
        return lines

    start, end = _find_class_block(lines, class_name)
    class_lines = lines[start:end]
    existing_keys = set(_member_signature_key(line) for line in class_lines)

    missing = []
    for line in member_lines:
        key = _member_signature_key(line)
        if key in existing_keys:
            continue
        missing.append(line)

    if not missing:
        return lines

    out = list(lines[:end])
    if out and out[-1].strip() != "":
        out.append("")
    out.extend(missing)
    out.extend(lines[end:])
    return out


def _patch_client_pyi(filename, base_import_line, class_name, base_class_name, extra_lines):
    lines = _read_lines(filename)
    lines = _ensure_import(lines, base_import_line)
    lines = _ensure_import(lines, "from typing import Any")
    lines = _replace_class_base(lines, class_name, base_class_name)
    lines = _ensure_class_members(lines, class_name, extra_lines)
    _write_lines(filename, lines)


def make_client_pyi():
    with chdir(CLIENT_DIR):
        make_pyi_device_client(
            filename=ASYNC_CLIENT_PYI,
            api_spec=cobotta_writer_api_spec,
            class_name=ASYNC_CLIENT_CLASS,
            async_mode=True,
        )
        _patch_client_pyi(
            filename=ASYNC_CLIENT_PYI,
            base_import_line=(
                "from ese774_frame.clients.async_device_client import AsyncDeviceClient"
            ),
            class_name=ASYNC_CLIENT_CLASS,
            base_class_name="AsyncDeviceClient",
            extra_lines=[],
        )

        make_pyi_device_client(
            filename=SYNC_CLIENT_PYI,
            api_spec=cobotta_writer_api_spec,
            class_name=SYNC_CLIENT_CLASS,
            async_mode=False,
        )
        _patch_client_pyi(
            filename=SYNC_CLIENT_PYI,
            base_import_line=(
                "from .async_cobotta_writer_client import AsyncCobottaWriterClient"
            ),
            class_name=SYNC_CLIENT_CLASS,
            base_class_name="AsyncCobottaWriterClient",
            extra_lines=[
                "    # --- methods defined in .py, not in api_spec ---",
                "    @staticmethod",
                "    def _sync_wrap(coro) -> Any: ...",
                "    def _register_sync_methods(self) -> None: ...",
                "    def close_client(self) -> None: ...",
            ],
        )


def make_router_pyi():
    with chdir(ROUTER_DIR):
        make_pyi_device_router(
            filename=ROUTER_PYI,
            api_spec=cobotta_writer_api_spec,
            class_name=ROUTER_CLASS,
        )


def make_clients_init_pyi():
    lines = [
        "from .async_cobotta_writer_client import AsyncCobottaWriterClient",
        "from .sync_cobotta_writer_client import SyncCobottaWriterClient",
        "",
        "__all__: list[str]",
        "",
    ]
    with chdir(CLIENT_DIR):
        _write_lines(CLIENT_INIT_PYI, lines)


def make_server_init_pyi():
    """server_fastapi/__init__.pyi に DeviceProxy overload と公開名を出力する。"""
    import_lines = [
        "from glyph_motion.server_fastapi.clients.async_cobotta_writer_client import AsyncCobottaWriterClient",
        "from glyph_motion.server_fastapi.clients.sync_cobotta_writer_client import SyncCobottaWriterClient",
        "from glyph_motion.server_fastapi.routers.font_bcap_cobotta_writer_router import FontBcapCobottaWriterRouter",
        "from glyph_motion.server_fastapi.server import create_server, run",
        "from glyph_motion.server_fastapi.spec_writer import cobotta_writer_api_spec",
    ]

    make_pyi_device_proxy(
        filename=SERVER_INIT_PYI,
        import_lines=import_lines,
        device_class=DEVICE_CLASS,
        sync_client_class_name=SYNC_CLIENT_CLASS,
        async_client_class_name=ASYNC_CLIENT_CLASS,
        aliases=DEVICE_ALIASES,
        all_names=[
            "DeviceProxy",
            "AsyncCobottaWriterClient",
            "SyncCobottaWriterClient",
            "FontBcapCobottaWriterRouter",
            "cobotta_writer_api_spec",
            "create_server",
            "run",
        ],
    )


def main():
    make_client_pyi()
    make_router_pyi()
    make_clients_init_pyi()
    make_server_init_pyi()


if __name__ == "__main__":
    main()
