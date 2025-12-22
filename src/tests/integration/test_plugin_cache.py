import pytest

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

pytestmark = pytest.mark.anyio


def test_plugin_caches_document_and_schema() -> None:
    from litestar import Litestar, websocket_listener

    @websocket_listener("/listen")
    async def listener(socket: object, data: str) -> str:
        raise RuntimeError

    plugin = AsyncAPIPlugin(config=AsyncAPIConfig(use_cache=True))
    app = Litestar(route_handlers=[listener], plugins=[plugin])

    doc1 = plugin.get_asyncapi(app)
    doc2 = plugin.get_asyncapi(app)
    assert doc1 is doc2

    schema1 = plugin.get_asyncapi_schema(app)
    schema2 = plugin.get_asyncapi_schema(app)
    assert schema1 is schema2

    plugin.invalidate_cache()
    doc3 = plugin.get_asyncapi(app)
    assert doc3 is not doc1
