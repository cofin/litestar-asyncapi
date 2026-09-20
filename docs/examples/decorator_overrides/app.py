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

import msgspec
from litestar import Litestar, websocket
from litestar.exceptions import WebSocketDisconnect

from litestar_asyncapi import (
    AsyncAPIConfig,
    AsyncAPIPlugin,
    DocsConfig,
    MessageDefinition,
    asyncapi_message,
    asyncapi_operation,
)
from litestar_asyncapi.spec import Server

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("Incoming", "handler")


@dataclass
class Incoming:
    value: int


@dataclass(slots=True)
class Reset:
    reset: bool


@asyncapi_operation(
    action="receive",
    operation_id="incoming_receive",
    summary="Inbound messages",
    description="Accept either an integer value or a reset command.",
    messages=[
        MessageDefinition(name="Incoming", payload=Incoming, content_type="application/json", examples=[{"value": 1}]),
        MessageDefinition(name="Reset", payload=Reset, content_type="application/json", examples=[{"reset": True}]),
    ],
)
@asyncapi_message(action="send", payload=dict[str, int | str], name="Result", content_type="application/json")
@websocket("/ws/overrides")
async def handler(socket: "WebSocket") -> None:
    """Handle incoming WebSocket messages with decorator overrides."""
    await socket.accept()
    try:
        while True:
            data = await socket.receive_json()
            if "reset" in data:
                msgspec.convert(data, type=Reset)
                value = 0
            else:
                value = msgspec.convert(data, type=Incoming).value
            response = {"received": value, "status": "processed"}
            await socket.send_json(response)
    except WebSocketDisconnect:
        pass


config = AsyncAPIConfig(
    title="Decorator Overrides",
    docs=DocsConfig(interactive=True),
    servers={"local": Server(host="localhost:8000", protocol="ws")},
)

app = Litestar(route_handlers=[handler], plugins=[AsyncAPIPlugin(config)])
