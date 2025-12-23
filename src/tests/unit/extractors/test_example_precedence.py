from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener

from litestar_asyncapi import AsyncAPIConfig, asyncapi_message
from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_decorator_examples_override_generated_examples() -> None:
    @dataclass
    class Payload:
        value: int

    @asyncapi_message(action="receive", payload=Payload, examples=[{"value": 123}])
    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[handler])
    config = AsyncAPIConfig(create_examples=True, random_seed=1)
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(), config=config)
    operations = {op.action: op for op in channels[0].operations}

    receive = operations[OperationAction.RECEIVE]
    send = operations[OperationAction.SEND]

    assert receive.message is not None
    assert receive.message.examples == [{"value": 123}]

    assert send.message is not None
    assert send.message.examples
