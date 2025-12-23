from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_plain_websocket_handler_produces_channel_without_operations() -> None:
    from litestar import Litestar, websocket

    @websocket("/plain")
    async def handler(socket: "WebSocket") -> None:
        return None

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    assert channel.address == "/plain"
    assert list(channel.operations) == []
