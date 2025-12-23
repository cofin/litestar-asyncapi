from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_examples_generated_for_listener_messages() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)
    by_action = {op.action: op for op in channels[0].operations}

    receive = by_action[OperationAction.RECEIVE]
    send = by_action[OperationAction.SEND]

    assert receive.message is not None
    assert receive.message.examples
    assert isinstance(receive.message.examples[0], dict)
    assert "value" in receive.message.examples[0]

    assert send.message is not None
    assert send.message.examples
    assert isinstance(send.message.examples[0], dict)


def test_examples_generated_for_stream_messages() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[stream])
    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)
    operation = channels[0].operations[0]

    assert operation.message is not None
    assert operation.message.examples
    assert isinstance(operation.message.examples[0], dict)
