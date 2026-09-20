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
    assert doc1 is not doc2
    assert doc1 == doc2

    schema1 = plugin.get_asyncapi_schema(app)
    schema2 = plugin.get_asyncapi_schema(app)
    assert schema1 is not schema2
    assert schema1 == schema2

    plugin.clear_cache()
    doc3 = plugin.get_asyncapi(app)
    assert doc3 is not doc1


def test_public_schema_mutation_cannot_poison_cache() -> None:
    from litestar import Litestar

    plugin = AsyncAPIPlugin()
    app = Litestar([], plugins=[plugin])
    schema = plugin.get_asyncapi_schema(app)
    schema["info"]["title"] = "poisoned"
    assert plugin.get_asyncapi_schema(app)["info"]["title"] == "AsyncAPI"


@pytest.mark.parametrize("use_cache", [False, True])
def test_plugin_rejects_second_application(use_cache: bool) -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    plugin = AsyncAPIPlugin(AsyncAPIConfig(use_cache=use_cache))
    first, second = Litestar([]), Litestar([])
    plugin.get_asyncapi(first)
    with pytest.raises(ImproperlyConfiguredException, match="application"):
        plugin.get_asyncapi_schema(second)


@pytest.mark.parametrize("use_cache", [False, True])
def test_all_document_accessors_are_defensive_and_clear_preserves_binding(use_cache: bool) -> None:
    import json

    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi.spec import Server

    plugin = AsyncAPIPlugin(
        AsyncAPIConfig(use_cache=use_cache, servers={"main": Server(host="original", protocol="ws")})
    )
    app = Litestar([])
    document = plugin.get_asyncapi(app)
    document.info.title = "poisoned"
    document.servers["main"].host = "poisoned"
    document.components.schemas["poisoned"] = False
    schema = plugin.get_asyncapi_schema(app)
    schema["servers"]["main"]["host"] = "poisoned"
    schema["info"]["title"] = "poisoned"
    assert plugin.get_asyncapi(app).servers["main"].host == "original"
    assert plugin.get_asyncapi_schema(app)["info"]["title"] == "AsyncAPI"
    assert json.loads(plugin.get_asyncapi_json(app))["servers"]["main"]["host"] == "original"
    plugin.clear_cache()
    with pytest.raises(ImproperlyConfiguredException, match="one application"):
        plugin.get_asyncapi(Litestar([]))
    assert plugin.get_asyncapi(app).info.title == "AsyncAPI"


@pytest.mark.parametrize("use_cache", [False, True])
def test_generation_is_lazy_and_cache_invalidation_is_explicit(monkeypatch, use_cache: bool) -> None:
    from litestar import Litestar

    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    original = AsyncAPIGenerator.build_asyncapi
    calls = []

    def build(generator):
        calls.append(generator.app)
        return original(generator)

    monkeypatch.setattr(AsyncAPIGenerator, "build_asyncapi", build)
    plugin = AsyncAPIPlugin(AsyncAPIConfig(use_cache=use_cache))
    app = Litestar([], plugins=[plugin], openapi_config=None)
    assert calls == []
    plugin.get_asyncapi(app)
    plugin.get_asyncapi_schema(app)
    plugin.get_asyncapi_json(app)
    assert len(calls) == (1 if use_cache else 3)
    plugin.config.title = "updated"
    assert plugin.get_asyncapi_schema(app)["info"]["title"] == ("AsyncAPI" if use_cache else "updated")
    plugin.clear_cache()
    assert plugin.get_asyncapi_schema(app)["info"]["title"] == "updated"


def test_request_host_and_nested_document_mutations_do_not_change_cached_json() -> None:
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi.spec import Components, Schema

    config = AsyncAPIConfig(components=Components(schemas={"Example": Schema(default={"nested": [None]})}))
    plugin = AsyncAPIPlugin(config)
    app = Litestar([], plugins=[plugin])
    document = plugin.get_asyncapi(app)
    document.components.schemas["Example"].default["nested"].append("poisoned")
    with TestClient(app) as client:
        first = client.get("/asyncapi/asyncapi.json", headers={"host": "first.invalid"})
        second = client.get("/asyncapi/asyncapi.json", headers={"host": "second.invalid"})
    assert first.content == second.content == plugin.get_asyncapi_json(app)
    assert first.json()["components"]["schemas"]["Example"]["default"] == {"nested": [None]}
