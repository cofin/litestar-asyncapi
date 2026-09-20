"""Tests for AsyncAPIPlaygroundRenderPlugin."""

import pytest

pytestmark = pytest.mark.anyio


def test_playground_init_defaults() -> None:
    """Playground should have default path /playground."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin()

    assert plugin.paths == ["/playground"]
    assert plugin.enable_validation is True
    assert plugin.theme == "light"


def test_playground_custom_path() -> None:
    """Playground should accept custom path."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin(path="/custom-playground")

    assert plugin.paths == ["/custom-playground"]


def test_playground_multiple_paths() -> None:
    """Playground should accept multiple paths."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin(path=["/play", "/test"])

    assert plugin.paths == ["/play", "/test"]


def test_playground_validation_toggle() -> None:
    """Playground should respect validation toggle."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin_enabled = AsyncAPIPlaygroundRenderPlugin(enable_validation=True)
    plugin_disabled = AsyncAPIPlaygroundRenderPlugin(enable_validation=False)

    assert plugin_enabled.enable_validation is True
    assert plugin_disabled.enable_validation is False


def test_playground_theme_option() -> None:
    """Playground should respect theme option."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    light_plugin = AsyncAPIPlaygroundRenderPlugin(theme="light")
    dark_plugin = AsyncAPIPlaygroundRenderPlugin(theme="dark")

    assert light_plugin.theme == "light"
    assert dark_plugin.theme == "dark"


def test_playground_html_uses_fetched_schema_and_inert_options() -> None:
    import json
    import re

    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    renderer = AsyncAPIPlaygroundRenderPlugin(theme="dark", enable_validation=False)
    app = Litestar(
        [], plugins=[AsyncAPIPlugin(AsyncAPIConfig(title="Test API", docs=DocsConfig(render_plugins=[renderer])))]
    )
    with TestClient(app) as client:
        response = client.get("/asyncapi/playground")
        assert response.status_code == 200
        assert "Test API - Playground" in response.text
        assert "#1a1a2e" in response.text
        match = re.search(r'<script id="asyncapi-config" type="application/json">(.*?)</script>', response.text)
        assert match is not None
        config = json.loads(match[1])
        assert config["options"]["enableValidation"] is False
        assert client.get(config["schemaUrl"]).json()["info"]["title"] == "Test API"
        assert client.get(config["entryUrl"]).status_code == 200


def test_playground_has_path_method() -> None:
    """Playground should correctly report path membership."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin(path=["/play", "/test"])

    assert plugin.has_path("/play") is True
    assert plugin.has_path("/test") is True
    assert plugin.has_path("/other") is False


def test_playground_integration_with_app() -> None:
    """Playground should be accessible when registered with an app."""
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    config = AsyncAPIConfig(
        title="Integration Test", docs=DocsConfig(render_plugins=[AsyncAPIPlaygroundRenderPlugin()])
    )
    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin(config)])

    with TestClient(app=app) as client:
        response = client.get("/asyncapi/playground")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "Integration Test - Playground" in response.text


def test_playground_requires_explicit_opt_in() -> None:
    """Default documentation must not expose an interactive console."""
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIPlugin

    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin()])

    with TestClient(app=app) as client:
        response = client.get("/asyncapi/playground")
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("text/html")
