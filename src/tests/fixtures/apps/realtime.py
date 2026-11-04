from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Literal

from litestar import Litestar, get, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.handlers.websocket_handlers.stream import websocket_stream
from litestar.response import ServerSentEvent

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig, asyncapi_message
from litestar_asyncapi.asyncapi.datastructures import ChannelDefinition, MessageDefinition, OperationDefinition

__all__ = ("app_3_0", "app_3_1")


@dataclass
class Metric:
    name: str
    value: float


@dataclass
class ChatMessage:
    text: str


@websocket_stream("/live/metrics")
async def metrics() -> AsyncGenerator[Metric, None]:
    yield Metric(name="cpu", value=0.5)


@websocket_listener("/chat/{room:int}")
async def chat(data: ChatMessage) -> ChatMessage:
    return data


@dataclass
class Order:
    order_id: str
    quantity: int


@dataclass
class Price:
    symbol: str
    amount: float


async def _events() -> AsyncGenerator[str, None]:
    yield "ping"


@asyncapi_message(action="send", payload=Price, name="price", examples=[Price(symbol="ACME", amount=1.5)])
@get("/prices/{symbol:str}")
async def prices(symbol: str) -> ServerSentEvent:
    return ServerSentEvent(_events())


@get("/live/metrics")
async def metrics_events() -> ServerSentEvent:
    return ServerSentEvent(_events())


def create_app(spec_version: Literal["3.0.0", "3.1.0"]) -> Litestar:
    config = AsyncAPIConfig(
        title="Realtime fixture",
        version="1.0.0",
        spec_version=spec_version,
        docs=DocsConfig(enabled=False),
        channel_payloads={"news": ChatMessage, "orders": Order},
        channels=[
            ChannelDefinition(
                key="audit",
                address="audit",
                description="Audit trail",
                extensions={"x-retention": "7d"},
                operations=[
                    OperationDefinition(
                        action="send",
                        operation_id="publishAudit",
                        messages=[MessageDefinition(name="entry", payload=str)],
                    )
                ],
            )
        ],
    )
    channels = ChannelsPlugin(
        MemoryChannelsBackend(), channels=["news"], create_ws_route_handlers=True, ws_handler_base_path="/ws/"
    )
    topics = ChannelsPlugin(MemoryChannelsBackend(), channels=["orders", "alerts"])
    return Litestar(
        route_handlers=[metrics, chat, prices, metrics_events], plugins=[channels, topics, AsyncAPIPlugin(config)]
    )


app_3_0 = create_app("3.0.0")
app_3_1 = create_app("3.1.0")
