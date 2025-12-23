from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_listener_handler_metadata_applied() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_listener(
        "/ws",
        summary="Listener Summary",
        description="Listener Description",
        operation_id="listener",
        signature_namespace={"Payload": Payload},
    )
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator())
    operations = {op.action: op for op in channels[0].operations}

    receive = operations[OperationAction.RECEIVE]
    send = operations[OperationAction.SEND]
    assert receive.summary == "Listener Summary"
    assert send.description == "Listener Description"
    assert receive.operation_id == "listener_receive"
    assert send.operation_id == "listener_send"


def test_stream_handler_metadata_applied() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_stream(
        "/stream",
        summary="Stream Summary",
        description="Stream Description",
        operation_id="stream",
        signature_namespace={"Payload": Payload},
    )
    async def stream() -> "AsyncGenerator[Payload, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[stream])
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator())
    operation = channels[0].operations[0]

    assert operation.summary == "Stream Summary"
    assert operation.description == "Stream Description"
    assert operation.operation_id == "stream"
