# /// script
# requires-python = ">=3.11"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Discover a WebSocket listener, a Server-Sent Event route and a ChannelsPlugin topic in one app."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from litestar import Litestar, get, websocket_listener
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.response import ServerSentEvent

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

__all__ = ("Order", "app", "chat", "order_events")


@dataclass
class Order:
    order_id: str
    total: float


@websocket_listener("/ws/chat")
async def chat(data: str) -> str:
    return data.upper()


async def order_stream(channels: ChannelsPlugin) -> AsyncGenerator[bytes, None]:
    async with channels.start_subscription(["orders"]) as subscriber:
        async for event in subscriber.iter_events():
            yield event


@get("/orders/events")
async def order_events(channels: ChannelsPlugin) -> ServerSentEvent:
    return ServerSentEvent(order_stream(channels))


config = AsyncAPIConfig(title="Order desk", channel_payloads={"orders": Order})

app = Litestar(
    route_handlers=[chat, order_events],
    plugins=[AsyncAPIPlugin(config), ChannelsPlugin(MemoryChannelsBackend(), channels=["orders"])],
)
