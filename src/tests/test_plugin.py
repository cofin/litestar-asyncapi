from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

pytestmark = pytest.mark.anyio


def test_plugin_instantiation_with_defaults() -> None:
    """Test that the plugin can be instantiated with default configuration."""
    from litestar_asyncapi import AsyncAPIPlugin

    plugin = AsyncAPIPlugin()
    assert plugin.config.title == "AsyncAPI"
    assert plugin.config.version == "1.0.0"
    assert plugin.config.description is None


def test_plugin_instantiation_with_config(asyncapi_config: "AsyncAPIConfig") -> None:
    """Test that the plugin can be instantiated with custom configuration."""
    from litestar_asyncapi import AsyncAPIPlugin

    plugin = AsyncAPIPlugin(config=asyncapi_config)
    assert plugin.config.title == "Test API"
    assert plugin.config.version == "1.0.0"
    assert plugin.config.description == "A test API"


def test_config_defaults() -> None:
    """Test that the configuration has sensible defaults."""
    from litestar_asyncapi import AsyncAPIConfig

    config = AsyncAPIConfig()
    assert config.title == "AsyncAPI"
    assert config.version == "1.0.0"
    assert config.description is None
    assert config.servers == {}


def test_plugin_with_litestar_app(app: "Litestar", asyncapi_plugin: "AsyncAPIPlugin") -> None:
    """Test that the plugin integrates with a Litestar application."""
    assert asyncapi_plugin in app.plugins
    assert asyncapi_plugin.config.title == "Test API"
