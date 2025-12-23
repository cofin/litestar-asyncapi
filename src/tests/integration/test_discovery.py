from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_websocket_extraction_across_handler_variants() -> None:
    from litestar import Litestar, websocket, websocket_listener
    from litestar.handlers.websocket_handlers.stream import websocket_stream

    @dataclass
    class Payload:
        value: int

    @websocket("/plain")
    async def plain(socket: "WebSocket") -> None:
        return None

    @websocket_listener("/listen/{room:int}", signature_namespace={"Payload": Payload})
    async def listener(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[plain, listener, stream])
    gen = AsyncAPISchemaGenerator()

    channels = extract_websocket_channels(app, schema_generator=gen)
    by_address = {c.address: c for c in channels}
    assert set(by_address) == {"/plain", "/listen/{room}", "/stream"}

    # Raw websockets now generate placeholder operations for both directions
    assert {op.action for op in by_address["/plain"].operations} == {
        OperationAction.RECEIVE,
        OperationAction.SEND,
    }
    assert {op.action for op in by_address["/listen/{room}"].operations} == {
        OperationAction.RECEIVE,
        OperationAction.SEND,
    }
    assert [op.action for op in by_address["/stream"].operations] == [OperationAction.SEND]

    assert by_address["/listen/{room}"].parameters is not None
    assert "room" in by_address["/listen/{room}"].parameters


def test_websocket_routes_discovered_from_nested_router() -> None:
    from litestar import Litestar, Router, websocket

    @websocket("/nested")
    async def nested(socket: "WebSocket") -> None:
        return None

    router = Router(path="/api", route_handlers=[nested])
    app = Litestar(route_handlers=[router])
    gen = AsyncAPISchemaGenerator()

    channels = extract_websocket_channels(app, schema_generator=gen)
    assert {c.address for c in channels} == {"/api/nested"}
