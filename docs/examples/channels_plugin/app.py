# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "litestar[standard]",
#     "litestar-asyncapi",
# ]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../../.." }
# ///
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from litestar import Litestar, post, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.dto import DataclassDTO

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.spec import Server

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("EchoPayload", "PublishPayload", "echo", "publish_message")


@dataclass
class EchoPayload:
    message: str


@dataclass
class PublishPayload:
    message: str


@websocket_listener("/ws/echo", dto=DataclassDTO[EchoPayload], signature_namespace={"EchoPayload": EchoPayload})
async def echo(socket: "WebSocket[Any, Any, Any]", data: EchoPayload) -> EchoPayload:
    return data


@post("/publish/{channel:str}")
async def publish_message(channel: str, data: PublishPayload, channels: ChannelsPlugin) -> dict[str, str]:
    """Publish a message to a channel.

    Args:
        channel: The channel name to publish to.
        data: The payload containing the message.
        channels: The ChannelsPlugin instance for publishing.

    Returns:
        Status dict with 'published' status and channel name.
    """
    channels.publish({"message": data.message}, channel)
    return {"status": "published", "channel": channel}


channels_plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=True)

config = AsyncAPIConfig(
    title="Channels Plugin",
    docs=DocsConfig(interactive=True),
    servers={"local": Server(host="localhost:8000", protocol="ws")},
)

app = Litestar(route_handlers=[echo, publish_message], plugins=[AsyncAPIPlugin(config), channels_plugin])
