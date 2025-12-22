from dataclasses import dataclass
from typing import Any

import pytest
from litestar import Litestar, websocket

from litestar_asyncapi import AsyncAPIPlugin, asyncapi_message, asyncapi_operation
from litestar_asyncapi.spec import OperationAction

pytestmark = pytest.mark.anyio


@dataclass
class InPayload:
    value: int


def test_plugin_generates_operations_from_decorator_only_plain_websocket() -> None:
    @asyncapi_operation(action="receive", operation_id="recv")
    @asyncapi_message(action="receive", payload=InPayload, name="Inbound")
    @websocket("/ws")
    async def handler(socket: Any) -> None:
        return None

    plugin = AsyncAPIPlugin()
    app = Litestar(route_handlers=[handler], plugins=[plugin])
    schema = plugin.get_asyncapi_schema(app)

    assert schema["asyncapi"] == "3.0.0"
    assert "channels" in schema and "/ws" in schema["channels"]
    assert "operations" in schema
    actions = {op["action"] for op in schema["operations"].values()}
    assert actions == {OperationAction.RECEIVE.value}
