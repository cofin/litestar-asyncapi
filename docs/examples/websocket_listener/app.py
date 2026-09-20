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
from typing import TYPE_CHECKING

from litestar import Litestar, websocket_listener
from litestar.dto import DataclassDTO

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.spec import Server

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("ChatMessage", "chat_listener")


@dataclass
class ChatMessage:
    room: str
    text: str


@websocket_listener("/ws/chat", dto=DataclassDTO[ChatMessage], signature_namespace={"ChatMessage": ChatMessage})
async def chat_listener(socket: "WebSocket", data: ChatMessage) -> ChatMessage:
    return ChatMessage(room=data.room, text=f"echo: {data.text}")


config = AsyncAPIConfig(
    title="Websocket Listener",
    docs=DocsConfig(interactive=True),
    servers={"local": Server(host="localhost:8000", protocol="ws")},
)

app = Litestar(route_handlers=[chat_listener], plugins=[AsyncAPIPlugin(config)])
