from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_plain_websocket_handler_produces_placeholder_operations() -> None:
    from litestar import Litestar, websocket

    @websocket("/plain")
    async def handler(socket: "WebSocket") -> None:
        return None

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    assert channel.address == "/plain"

    # Raw websockets now produce placeholder operations for both directions
    assert len(channel.operations) == 2
    actions = {op.action for op in channel.operations}
    assert actions == {OperationAction.RECEIVE, OperationAction.SEND}

    # Verify placeholder messages have descriptive content
    for op in channel.operations:
        assert op.message is not None
        assert op.message.description is not None
        assert "raw websocket" in op.message.description.lower()
