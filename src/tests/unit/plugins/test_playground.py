"""Tests for AsyncAPIPlaygroundRenderPlugin."""

from unittest.mock import MagicMock

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


def test_playground_renders_html() -> None:
    """Playground should render valid HTML."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin()

    mock_request = MagicMock()
    schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "channels": {"/ws/test": {"description": "Test channel"}},
    }

    result = plugin.render(mock_request, schema)

    assert isinstance(result, bytes)
    html = result.decode("utf-8")
    assert "<!DOCTYPE html>" in html
    assert "Test API - Playground" in html


def test_playground_includes_channels() -> None:
    """Playground should list all channels from spec."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin()

    mock_request = MagicMock()
    schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "channels": {
            "/ws/one": {"description": "First channel"},
            "/ws/two": {"description": "Second channel"},
        },
    }

    result = plugin.render(mock_request, schema)
    html = result.decode("utf-8")

    assert "/ws/one" in html
    assert "/ws/two" in html


def test_playground_escapes_title() -> None:
    """Playground should HTML escape the title to prevent XSS."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin()

    mock_request = MagicMock()
    schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "<script>alert('xss')</script>", "version": "1.0.0"},
        "channels": {},
    }

    result = plugin.render(mock_request, schema)
    html = result.decode("utf-8")

    assert "<script>alert('xss')</script>" not in html
    assert "&lt;script&gt;" in html


def test_playground_dark_theme() -> None:
    """Playground should render dark theme colors."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin(theme="dark")

    mock_request = MagicMock()
    schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "channels": {},
    }

    result = plugin.render(mock_request, schema)
    html = result.decode("utf-8")

    assert "#1a1a2e" in html  # Dark theme background color


def test_playground_validation_disabled_in_js() -> None:
    """Playground should set enableValidation to false when disabled."""
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    plugin = AsyncAPIPlaygroundRenderPlugin(enable_validation=False)

    mock_request = MagicMock()
    schema = {
        "asyncapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "channels": {},
    }

    result = plugin.render(mock_request, schema)
    html = result.decode("utf-8")

    assert "const enableValidation = false" in html


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

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin
    from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin

    config = AsyncAPIConfig(
        title="Integration Test",
        render_plugins=[AsyncAPIPlaygroundRenderPlugin()],
    )
    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin(config)])

    with TestClient(app=app) as client:
        response = client.get("/asyncapi/playground")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "Integration Test - Playground" in response.text


def test_playground_default_in_config() -> None:
    """Playground should be included in default render plugins."""
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIPlugin

    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin()])

    with TestClient(app=app) as client:
        response = client.get("/asyncapi/playground")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
