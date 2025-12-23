from dataclasses import dataclass
from typing import Any

import pytest
from litestar import Litestar, websocket

from litestar_asyncapi import asyncapi_message, asyncapi_operation
from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

pytestmark = pytest.mark.anyio


@dataclass
class InPayload:
    value: int


@dataclass
class OutPayload:
    ok: bool


def test_decorator_only_plain_websocket_creates_operations() -> None:
    @asyncapi_operation(action="receive", operation_id="recv", summary="inbound")
    @asyncapi_message(action="receive", payload=InPayload, name="Inbound")
    @asyncapi_operation(action="send", operation_id="send", summary="outbound")
    @asyncapi_message(action="send", payload=OutPayload, name="Outbound")
    @websocket("/ws")
    async def handler(socket: Any) -> None:
        return None

    app = Litestar(route_handlers=[handler])
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator())
    assert len(channels) == 1
    assert channels[0].address == "/ws"

    by_action = {op.action: op for op in channels[0].operations}
    assert set(by_action) == {OperationAction.RECEIVE, OperationAction.SEND}
    receive = by_action[OperationAction.RECEIVE]
    assert receive.operation_id == "recv"
    assert receive.summary == "inbound"
    assert receive.message is not None
    assert receive.message.name == "Inbound"

    send = by_action[OperationAction.SEND]
    assert send.operation_id == "send"
    assert send.summary == "outbound"
    assert send.message is not None
    assert send.message.name == "Outbound"
