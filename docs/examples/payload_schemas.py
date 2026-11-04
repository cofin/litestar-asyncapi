# /// script
# requires-python = ">=3.11"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Generate Draft07 payload schemas with tuple bounds and an explicit example."""

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from litestar import Litestar, websocket_stream

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, asyncapi_message

__all__ = ("Reading", "app", "readings")


@dataclass
class Reading:
    sensor: str
    position: tuple[float, float]
    tags: tuple[str, ...]
    note: str | None = None


EXAMPLE = Reading(sensor="roof-1", position=(52.52, 13.40), tags=("outdoor",))


@asyncapi_message(action="send", payload=Reading, name="reading", examples=[EXAMPLE])
@websocket_stream("/ws/readings")
async def readings() -> AsyncGenerator[Reading, None]:
    while True:
        yield EXAMPLE
        await asyncio.sleep(1)


app = Litestar(route_handlers=[readings], plugins=[AsyncAPIPlugin(AsyncAPIConfig(title="Sensor readings"))])
