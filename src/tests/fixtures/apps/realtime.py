from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Literal

from litestar import Litestar, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
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


def create_app(spec_version: Literal["3.0.0", "3.1.0"]) -> Litestar:
    config = AsyncAPIConfig(
        title="Realtime fixture",
        version="1.0.0",
        spec_version=spec_version,
        docs=DocsConfig(enabled=False),
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
    return Litestar(route_handlers=[metrics, chat], plugins=[channels, AsyncAPIPlugin(config)])


app_3_0 = create_app("3.0.0")
app_3_1 = create_app("3.1.0")
