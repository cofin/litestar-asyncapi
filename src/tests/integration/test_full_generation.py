import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

pytestmark = pytest.mark.anyio


def test_full_document_schema_generation() -> None:
    from litestar import Litestar, websocket_listener

    @websocket_listener("/listen")
    async def listener(socket: object, data: str) -> str:
        raise RuntimeError

    app = Litestar(route_handlers=[listener])
    from litestar_asyncapi import AsyncAPIConfig

    schema = AsyncAPIGenerator(app=app, config=AsyncAPIConfig(title="My API", version="0.1.0")).build_schema()
    assert schema["asyncapi"] == "3.0.0"
    assert schema["info"]["title"] == "My API"
    assert schema.get("channels")
    assert schema.get("operations")
