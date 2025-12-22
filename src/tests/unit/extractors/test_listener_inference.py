from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi._asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi._asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction, Reference

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_listener_infers_receive_and_send_operations() -> None:
    attrs = pytest.importorskip("attrs")
    from litestar import Litestar, websocket_listener

    @attrs.define
    class InPayload:
        user_id: int

    @attrs.define
    class OutPayload:
        ok: bool

    @websocket_listener("/listen", signature_namespace={"InPayload": InPayload, "OutPayload": OutPayload})
    async def handler(socket: "WebSocket", data: InPayload) -> OutPayload:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    actions = {op.action for op in channel.operations}
    assert actions == {OperationAction.RECEIVE, OperationAction.SEND}

    receive = next(op for op in channel.operations if op.action is OperationAction.RECEIVE)
    send = next(op for op in channel.operations if op.action is OperationAction.SEND)
    assert receive.message is not None and isinstance(receive.message.payload, Reference)
    assert send.message is not None and isinstance(send.message.payload, Reference)

    components = gen.schema_registry.generate_components_schemas()
    assert any(k.endswith("InPayload") for k in components)
    assert any(k.endswith("OutPayload") for k in components)


def test_listener_omits_send_operation_for_none_return() -> None:
    from litestar import Litestar, websocket_listener

    @websocket_listener("/listen-none")
    async def handler(socket: "WebSocket", data: str) -> None:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    assert [op.action for op in channel.operations] == [OperationAction.RECEIVE]
