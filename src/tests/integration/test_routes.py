import pytest
from litestar import Litestar
from litestar.testing import TestClient

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig

pytestmark = pytest.mark.anyio


def test_docs_routes_exist_and_have_expected_media_types() -> None:
    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(yaml=True)))])

    with TestClient(app=app) as client:
        json_response = client.get("/asyncapi/asyncapi.json")
        assert json_response.status_code == 200
        assert json_response.headers["content-type"].startswith("application/vnd.asyncapi+json")
        assert json_response.json()["asyncapi"] == "3.1.0"

        yaml_response = client.get("/asyncapi/asyncapi.yaml")
        assert yaml_response.status_code == 200
        assert yaml_response.headers["content-type"].startswith("application/vnd.asyncapi+yaml")
        assert "asyncapi:" in yaml_response.text

        ui_response = client.get("/asyncapi/")
        assert ui_response.status_code == 200
        assert ui_response.headers["content-type"].startswith("text/html")
        assert "assets/bootstrap.js" in ui_response.text


def test_duplicate_renderer_paths_are_rejected() -> None:
    from litestar_asyncapi.plugins import JsonRenderPlugin

    with pytest.raises(ValueError, match="Duplicate documentation"):
        DocsConfig(render_plugins=[JsonRenderPlugin(path="/same"), JsonRenderPlugin(path="/same/")])


def test_docs_links_use_named_routes_and_external_bootstrap() -> None:
    app = Litestar([], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(path="/events", yaml=True)))])
    with TestClient(app, root_path="/gateway") as client:
        response = client.get("/events/")
        assert response.status_code == 200
        assert "/gateway/events/asyncapi.json" in response.text
        assert "/gateway/events/assets/bootstrap.js" in response.text
        assert 'type="application/json"' in response.text
        assert "const schema" not in response.text
        assert client.get("/events/assets/bootstrap.js").status_code == 200


def test_docs_guards_cover_schema_ui_playground_and_assets() -> None:
    from litestar.exceptions import NotAuthorizedException

    def guard(connection, handler) -> None:
        if connection.headers.get("authorization") != "test-token":
            raise NotAuthorizedException

    app = Litestar(
        [], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(guards=[guard], yaml=True, interactive=True)))]
    )
    with TestClient(app) as client:
        for path in (
            "/",
            "/asyncapi.json",
            "/asyncapi.yaml",
            "/playground",
            "/assets/bootstrap.js",
            "/assets/ui/manifest.json",
        ):
            assert client.get("/asyncapi" + path).status_code == 401
            assert client.get("/asyncapi" + path, headers={"authorization": "test-token"}).status_code == 200
        assert client.head("/asyncapi/assets/bootstrap.js").status_code == 401
        assert client.get("/asyncapi/assets/../config.py", headers={"authorization": "test-token"}).status_code == 404


def test_docs_under_asgi_mount_with_accumulated_root_path() -> None:
    from litestar import asgi
    from litestar.types import Receive, Scope, Send

    inner = Litestar([], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(path="/events", interactive=True)))])

    @asgi("/service", is_mount=True, copy_scope=True)
    async def mounted(scope: Scope, receive: Receive, send: Send) -> None:
        scope["root_path"] = scope.get("root_path", "") + "/service"
        await inner(scope, receive, send)

    outer = Litestar([mounted])
    with TestClient(outer, root_path="/gateway") as client:
        response = client.get("/service/events/")
        assert response.status_code == 200
        assert "/gateway/service/events/asyncapi.json" in response.text
        assert "/gateway/service/events/playground" in response.text
        assert client.get("/service/events/assets/bootstrap.js").status_code == 200


def test_docs_dependencies_are_available_to_native_renderer_routes() -> None:
    from litestar import get
    from litestar.di import Provide

    from litestar_asyncapi.plugins import AsyncAPIRenderPlugin

    class CustomRenderer(AsyncAPIRenderPlugin):
        def render(self, request, openapi_schema) -> bytes:
            return b"custom"

        def receive_router(self, router) -> None:
            @get("/dependency", sync_to_thread=False)
            def dependency(token: str) -> dict[str, str]:
                return {"token": token}

            router.register(dependency)

    config = DocsConfig(
        render_plugins=[CustomRenderer(path="/custom", media_type="text/plain")],
        dependencies={"token": Provide(lambda: "resolved", sync_to_thread=False)},
    )
    with TestClient(Litestar([], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=config))])) as client:
        assert client.get("/asyncapi/dependency").json() == {"token": "resolved"}


def test_distinct_renderers_cannot_claim_the_same_normalized_path() -> None:
    from litestar_asyncapi.plugins import JsonRenderPlugin, YamlRenderPlugin

    with pytest.raises(ValueError, match="Duplicate documentation route path"):
        DocsConfig(render_plugins=[JsonRenderPlugin(path="/schema"), YamlRenderPlugin(path="/schema/")])


def test_docs_under_native_nested_router() -> None:
    from litestar import Router

    plugin = AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(enabled=False)))
    app = Litestar([Router("/service", route_handlers=[plugin.create_docs_router()])], plugins=[plugin])
    with TestClient(app, root_path="/gateway") as client:
        response = client.get("/service/asyncapi/")
        assert response.status_code == 200
        assert "/gateway/service/asyncapi/asyncapi.json" in response.text
        assert client.get("/service/asyncapi/assets/bootstrap.js").status_code == 200
