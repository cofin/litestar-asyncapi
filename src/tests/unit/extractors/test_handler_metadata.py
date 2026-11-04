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


def test_decorator_added_operation_receives_handler_metadata_and_docstring() -> None:
    from litestar_asyncapi import AsyncAPIConfig, MessageDefinition, asyncapi_operation
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @asyncapi_operation(action="receive", messages=[MessageDefinition(name="Ping", payload=str)])
    @websocket_stream("/stream", summary="Stream Summary", operation_id="stream")
    async def stream() -> "AsyncGenerator[int, None]":
        """Stream documentation."""
        yield 1

    config = AsyncAPIConfig(use_handler_docstrings=True)
    operations = AsyncAPIGenerator(Litestar([stream]), config).build_schema()["operations"]
    assert set(operations) == {"stream_receive", "stream_send"}
    for operation in operations.values():
        assert operation["summary"] == "Stream Summary"
        assert operation["description"] == "Stream documentation."


def test_decorator_metadata_wins_over_handler_metadata() -> None:
    from litestar import websocket

    from litestar_asyncapi import AsyncAPIConfig, MessageDefinition, asyncapi_operation
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @asyncapi_operation(
        action="send",
        operation_id="outbound",
        summary="Decorator Summary",
        messages=[MessageDefinition(name="Pong", payload=int)],
    )
    @asyncapi_operation(action="receive", messages=[MessageDefinition(name="Ping", payload=str)])
    @websocket("/raw", summary="Raw Summary", description="Raw Description", operation_id="raw")
    async def raw(socket: "WebSocket") -> None:
        """Raw documentation."""

    config = AsyncAPIConfig(use_handler_docstrings=True)
    operations = AsyncAPIGenerator(Litestar([raw]), config).build_schema()["operations"]
    assert set(operations) == {"outbound", "raw_receive"}
    assert operations["outbound"]["summary"] == "Decorator Summary"
    assert operations["outbound"]["description"] == "Raw Description"
    assert operations["raw_receive"]["summary"] == "Raw Summary"
