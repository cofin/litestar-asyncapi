from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.datastructures import DiscoverySource
from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_websocket_routes_are_discovered() -> None:
    from litestar import Litestar, websocket

    @websocket("/ws/{room:int}")
    async def handler(socket: "WebSocket") -> None:
        return None

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channels = extract_websocket_channels(app, schema_generator=gen)
    assert [c.address for c in channels] == ["/ws/{room}"]
    assert channels[0].source is DiscoverySource.WEBSOCKET
