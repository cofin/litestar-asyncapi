from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIConfig, asyncapi_operation
from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_docstrings_applied_to_listener_operations() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        """Listener documentation.

        Raises:
            RuntimeError: Always raised.
        """
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    config = AsyncAPIConfig(use_handler_docstrings=True)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)

    for operation in channels[0].operations:
        assert operation.description is not None
        assert "Listener documentation." in operation.description
        assert "Raises:" in operation.description


def test_docstrings_applied_to_stream_operations() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        """Stream documentation.

        Yields:
            Payload: The example payload.
        """
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[stream])
    config = AsyncAPIConfig(use_handler_docstrings=True)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)

    description = channels[0].operations[0].description
    assert description is not None
    assert "Stream documentation." in description
    assert "Yields:" in description


def test_docstring_does_not_override_decorators() -> None:
    @dataclass
    class Payload:
        value: int

    @asyncapi_operation(action="receive", description="Decorator Description")
    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        """Handler documentation.

        Raises:
            RuntimeError: Always raised.
        """
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    config = AsyncAPIConfig(use_handler_docstrings=True)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)
    by_action = {op.action: op for op in channels[0].operations}

    assert by_action[OperationAction.RECEIVE].description == "Decorator Description"
    send_description = by_action[OperationAction.SEND].description
    assert send_description is not None
    assert "Handler documentation." in send_description
    assert "Raises:" in send_description
