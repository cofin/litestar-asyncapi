from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import AsyncAPI, OperationAction, Reference

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_generator_builds_document_with_channels_and_operations() -> None:
    from litestar import Litestar, websocket_listener
    from litestar.handlers.websocket_handlers.stream import websocket_stream

    @dataclass
    class Payload:
        value: int

    @websocket_listener("/listen", signature_namespace={"Payload": Payload})
    async def listener(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[listener, stream])

    from litestar_asyncapi import AsyncAPIConfig

    config = AsyncAPIConfig(title="Test", version="1.0.0", description="desc")
    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()

    assert isinstance(document, AsyncAPI)
    assert document.asyncapi == "3.0.0"
    assert document.info.title == "Test"
    assert document.default_content_type == "application/json"
    assert "/listen" in document.channels
    assert "/stream" in document.channels
    assert {op.action for op in document.operations.values()} == {OperationAction.RECEIVE, OperationAction.SEND}

    receive = next(op for op in document.operations.values() if op.action is OperationAction.RECEIVE)
    assert receive.messages is not None
    assert isinstance(receive.messages[0], Reference)
    channel = document.channels["/listen"]
    assert channel.messages is not None
    message_key = receive.messages[0].ref.split("/")[-1]
    assert message_key in channel.messages


def test_generator_ensures_unique_operation_ids_for_channels_plugin() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=False)
    app = Litestar(route_handlers=[], plugins=[plugin])
    config = AsyncAPIConfig(include_websocket_routes=False, include_channels_plugin=True)

    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()
    operation_ids = [op.operation_id for op in document.operations.values()]

    assert all(operation_ids)
    assert len(operation_ids) == len(set(operation_ids))
