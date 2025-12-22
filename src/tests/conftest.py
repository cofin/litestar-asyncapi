from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Return the async backend to use for tests."""
    return "asyncio"


@pytest.fixture
def asyncapi_config() -> "AsyncAPIConfig":
    """Return a default AsyncAPI configuration for testing."""
    from litestar_asyncapi import AsyncAPIConfig

    return AsyncAPIConfig(
        title="Test API",
        version="1.0.0",
        description="A test API",
    )


@pytest.fixture
def asyncapi_plugin(asyncapi_config: "AsyncAPIConfig") -> "AsyncAPIPlugin":
    """Return an AsyncAPI plugin instance for testing."""
    from litestar_asyncapi import AsyncAPIPlugin

    return AsyncAPIPlugin(config=asyncapi_config)


@pytest.fixture
def app(asyncapi_plugin: "AsyncAPIPlugin") -> "Litestar":
    """Return a Litestar application with the AsyncAPI plugin."""
    from litestar import Litestar

    return Litestar(plugins=[asyncapi_plugin])
