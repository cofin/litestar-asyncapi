# /// script
# requires-python = ">=3.10"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Document an HTTP route that streams Server-Sent Events."""

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from litestar import Litestar, get
from litestar.response import ServerSentEvent
from litestar.serialization import encode_json

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, asyncapi_message
from litestar_asyncapi.spec import Server

__all__ = ("Price", "app", "prices")


@dataclass
class Price:
    symbol: str
    amount: float


async def price_updates(symbol: str) -> AsyncGenerator[str, None]:
    for tick in range(3):
        yield encode_json(Price(symbol=symbol, amount=100 + tick)).decode()
        await asyncio.sleep(1)


@asyncapi_message(action="send", payload=Price, name="price", summary="Latest price for a symbol")
@get("/prices/{symbol:str}")
async def prices(symbol: str) -> ServerSentEvent:
    return ServerSentEvent(price_updates(symbol))


config = AsyncAPIConfig(title="Price stream", servers={"local": Server(host="localhost:8000", protocol="http")})

app = Litestar(route_handlers=[prices], plugins=[AsyncAPIPlugin(config)])
