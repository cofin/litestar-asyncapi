from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi import AsyncAPIConfig
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

    with pytest.warns(UserWarning, match="cannot infer the raw WebSocket"):
        channels = extract_websocket_channels(
            app, schema_generator=gen, config=AsyncAPIConfig(include_raw_websocket_routes=True)
        )
    by_address = {c.address: c for c in channels}
    assert set(by_address) == {"/plain", "/listen/{room}", "/stream"}

    # Raw websockets now generate placeholder operations for both directions
    assert {op.action for op in by_address["/plain"].operations} == {OperationAction.RECEIVE, OperationAction.SEND}
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

    with pytest.warns(UserWarning, match="cannot infer the raw WebSocket"):
        channels = extract_websocket_channels(
            app, schema_generator=gen, config=AsyncAPIConfig(include_raw_websocket_routes=True)
        )
    assert {c.address for c in channels} == {"/api/nested"}


def test_websocket_routes_discovered_from_deeply_nested_router() -> None:
    from litestar import Litestar, Router, websocket

    @websocket("/deep")
    async def deep(socket: "WebSocket") -> None:
        return None

    inner = Router(path="/inner", route_handlers=[deep])
    outer = Router(path="/outer", route_handlers=[inner])
    app = Litestar(route_handlers=[outer])
    gen = AsyncAPISchemaGenerator()

    with pytest.warns(UserWarning, match="cannot infer the raw WebSocket"):
        channels = extract_websocket_channels(
            app, schema_generator=gen, config=AsyncAPIConfig(include_raw_websocket_routes=True)
        )
    assert {c.address for c in channels} == {"/outer/inner/deep"}


@pytest.mark.parametrize("mode", ["text", "binary"])
@pytest.mark.parametrize("kind", ["text", "bytes", "json"])
def test_listener_contract_matches_actual_frames(mode: str, kind: str) -> None:
    import json

    from litestar import Litestar, Router, websocket_listener
    from litestar.testing import TestClient

    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    payload_type = {"text": str, "bytes": bytes, "json": tuple[int, str]}[kind]

    @websocket_listener("/echo", receive_mode=mode, send_mode=mode)
    async def echo(data: payload_type) -> payload_type:
        return data

    app = Litestar([Router("/nested", route_handlers=[echo])])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    expected = {"text": "hello", "bytes": "hello", "json": '[7,"seven"]'}[kind]
    with TestClient(app) as client, client.websocket_connect("/nested/echo") as socket:
        if mode == "text":
            socket.send_text(expected)
            received = socket.receive_text()
        else:
            socket.send_bytes(expected.encode())
            received = socket.receive_bytes().decode()
    assert json.loads(received) == [7, "seven"] if kind == "json" else received == expected
    for message in document["channels"]["/nested/echo"]["messages"].values():
        assert message["x-websocket-mode"] == mode
        assert (
            message["contentType"]
            == {"text": "text/plain", "bytes": "application/octet-stream", "json": "application/json"}[kind]
        )
        if kind == "json":
            assert message["payload"]["minItems"] == message["payload"]["maxItems"] == 2


@pytest.mark.parametrize("mode", ["text", "binary"])
def test_stream_contract_matches_native_serialization(mode: str) -> None:
    from litestar import Litestar
    from litestar.handlers.websocket_handlers.stream import websocket_stream
    from litestar.testing import TestClient

    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @websocket_stream("/values", mode=mode)
    async def values() -> "AsyncGenerator[dict[str, int], None]":
        yield {"value": 1}

    app = Litestar([values])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    with TestClient(app) as client, client.websocket_connect("/values") as socket:
        assert socket.receive_json(mode=mode) == {"value": 1}
    message = next(iter(document["channels"]["/values"]["messages"].values()))
    assert message["contentType"] == "application/json"
    assert message["x-websocket-mode"] == mode


def test_explicit_frame_extension_and_layered_visibility_win() -> None:
    from litestar import Litestar, Router, websocket_listener

    from litestar_asyncapi import asyncapi_message
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @asyncapi_message(action="receive", extensions={"x-websocket-mode": "custom"})
    @websocket_listener("/visible", opt={"include_in_schema": True}, receive_mode="binary")
    async def visible(data: str) -> None:
        return None

    @websocket_listener("/hidden")
    async def hidden(data: str) -> None:
        return None

    app = Litestar([Router("/outer", route_handlers=[visible, hidden], opt={"include_in_schema": False})])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    assert set(document["channels"]) == {"/outer/visible"}
    message = next(iter(document["channels"]["/outer/visible"]["messages"].values()))
    assert message["x-websocket-mode"] == "custom"


def test_native_return_dto_schema_matches_transferred_payload() -> None:
    from litestar import Litestar, websocket_listener
    from litestar.dto import DataclassDTO, DTOConfig
    from litestar.testing import TestClient

    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @dataclass
    class Model:
        value: int
        secret: str

    class PublicDTO(DataclassDTO[Model]):
        config = DTOConfig(exclude={"secret"})

    @websocket_listener("/dto", return_dto=PublicDTO, signature_namespace={"Model": Model})
    async def handler(data: int) -> Model:
        return Model(value=data, secret="hidden")

    app = Litestar([handler], openapi_config=None)
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    send = next(message for name, message in document["channels"]["/dto"]["messages"].items() if name.endswith("send"))
    component = document["components"]["schemas"][send["payload"]["$ref"].rsplit("/", 1)[-1]]
    assert set(component["properties"]) == {"value"}
    with pytest.warns(UserWarning, match="Omitting automatic AsyncAPI example for native DTO"):
        generated = AsyncAPIGenerator(app, AsyncAPIConfig(create_examples=True)).build_schema()
    output = next(
        message for name, message in generated["channels"]["/dto"]["messages"].items() if name.endswith("send")
    )
    assert "examples" not in output
    with TestClient(app) as client, client.websocket_connect("/dto") as socket:
        socket.send_json(3)
        assert socket.receive_json() == {"value": 3}


def test_mixed_stream_does_not_claim_json_for_raw_text() -> None:
    from litestar import Litestar
    from litestar.handlers.websocket_handlers.stream import websocket_stream
    from litestar.testing import TestClient

    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @websocket_stream("/mixed")
    async def mixed() -> "AsyncGenerator[str | int, None]":
        yield "unquoted text"
        yield 12

    app = Litestar([mixed])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    assert "defaultContentType" not in document
    message = next(iter(document["channels"]["/mixed"]["messages"].values()))
    assert "contentType" not in message
    with TestClient(app) as client, client.websocket_connect("/mixed") as socket:
        assert socket.receive_text() == "unquoted text"
        assert socket.receive_text() == "12"
    assert (
        AsyncAPIGenerator(app, AsyncAPIConfig(default_content_type="application/custom")).build_schema()[
            "defaultContentType"
        ]
        == "application/custom"
    )
