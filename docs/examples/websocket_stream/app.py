# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "litestar[standard]",
#     "litestar-asyncapi",
# ]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../../.." }
# ///
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, websocket_stream

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.spec import Server

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

__all__ = ("StreamItem", "stream_items")


@dataclass
class StreamItem:
    value: int


@websocket_stream("/ws/stream", signature_namespace={"StreamItem": StreamItem})
async def stream_items() -> "AsyncGenerator[StreamItem, None]":
    i = 0
    while True:
        yield StreamItem(value=i)
        i += 1
        await asyncio.sleep(1)


config = AsyncAPIConfig(
    title="Websocket Stream",
    docs=DocsConfig(interactive=True),
    servers={"local": Server(host="localhost:8000", protocol="ws")},
)

app = Litestar(route_handlers=[stream_items], plugins=[AsyncAPIPlugin(config)])
