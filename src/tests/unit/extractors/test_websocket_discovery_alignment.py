from litestar import Litestar, websocket
from litestar.handlers.websocket_handlers import WebsocketRouteHandler
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient

from litestar_asyncapi.asyncapi.extractors.websocket import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


def test_should_respect_include_in_schema_opt() -> None:
    @websocket("/included")
    async def included_handler(socket: WebsocketRouteHandler) -> None:
        await socket.accept()
        await socket.close()

    @websocket("/excluded", include_in_schema=False)
    async def excluded_handler(socket: WebsocketRouteHandler) -> None:
        await socket.accept()
        await socket.close()

    app = Litestar(route_handlers=[included_handler, excluded_handler])
    generator = AsyncAPISchemaGenerator()
    
    channels = extract_websocket_channels(app, schema_generator=generator)
    
    addresses = {c.address for c in channels}
    assert "/included" in addresses
    assert "/excluded" not in addresses
