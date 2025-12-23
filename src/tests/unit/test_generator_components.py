import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

pytestmark = pytest.mark.anyio


def test_generator_populates_components_schemas_for_attrs_payloads() -> None:
    attrs = pytest.importorskip("attrs")
    from litestar import Litestar, websocket_listener

    @attrs.define
    class Payload:
        value: int

    @websocket_listener("/listen", signature_namespace={"Payload": Payload})
    async def listener(socket: object, data: Payload) -> Payload:
        raise RuntimeError

    app = Litestar(route_handlers=[listener])
    from litestar_asyncapi import AsyncAPIConfig

    document = AsyncAPIGenerator(app=app, config=AsyncAPIConfig()).build_asyncapi()
    assert document.components.schemas
    assert any(k.endswith("Payload") for k in document.components.schemas)
