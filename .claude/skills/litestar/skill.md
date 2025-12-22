# Litestar Framework Skill

## Quick Reference

### Plugin Development

```python
from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig


class MyConfig:
    pass


class MyPlugin(InitPluginProtocol):
    """Plugin implementing InitPluginProtocol."""

    __slots__ = ("_config",)

    def __init__(self, config: "MyConfig | None" = None) -> None:
        self._config = config or MyConfig()

    @property
    def config(self) -> "MyConfig":
        return self._config

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        # Add routes, middleware, etc.
        return app_config
```

### WebSocket Handler

```python
from typing import TYPE_CHECKING

from litestar import Litestar, websocket
from litestar.handlers import WebsocketListener

if TYPE_CHECKING:
    from litestar import WebSocket


@websocket("/ws")
async def websocket_handler(socket: "WebSocket") -> None:
    """WebSocket handler."""
    await socket.accept()
    async for message in socket.iter_json():
        await socket.send_json({"received": message})


# Or using WebsocketListener
class MyWebSocketHandler(WebsocketListener):
    path = "/ws"

    async def on_accept(self, socket: "WebSocket") -> None:
        pass

    async def on_receive(self, data: str) -> str:
        return f"received: {data}"
```

### Route Handler

```python
from litestar import Litestar, get, post
from litestar.datastructures import State


@get("/items")
async def list_items(state: State) -> list[dict]:
    """List all items."""
    return state.items


@post("/items")
async def create_item(data: ItemCreate, state: State) -> Item:
    """Create a new item."""
    item = Item(**data.dict())
    state.items.append(item)
    return item
```

### Testing

```python
from litestar.testing import TestClient


def test_endpoint() -> None:
    with TestClient(app=app) as client:
        response = client.get("/items")
        assert response.status_code == 200
```

## Context7 Lookups

```python
# Resolve Litestar library ID
mcp__context7__resolve-library-id(libraryName="litestar")
# Returns: /litestar-org/litestar

# Get plugin documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="plugins",
    mode="code"
)

# Get WebSocket documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="websocket",
    mode="code"
)

# Get routing documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="routing",
    mode="code"
)

# Get testing documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="testing",
    mode="code"
)
```

## Project-Specific Patterns

### Plugin in This Project

See `src/litestar_asyncapi/plugin.py` for the project's plugin implementation.

Key patterns:
- `__slots__` for memory efficiency
- Lazy imports inside methods
- Property for config access
- TYPE_CHECKING for type-only imports

### Configuration Dataclass

See `src/litestar_asyncapi/config.py` for configuration pattern.

Key patterns:
- Dataclass with defaults
- Field docstrings as inline comments
- `field(default_factory=...)` for mutable defaults

### Test Fixtures

See `src/tests/conftest.py` for fixture patterns.

Key patterns:
- `anyio_backend` fixture
- Plugin and config fixtures
- App fixture with plugin

## Common Tasks

### Add a Route via Plugin

```python
def on_app_init(self, app_config: AppConfig) -> AppConfig:
    from litestar import get

    @get("/asyncapi.json")
    async def asyncapi_schema() -> dict:
        return self._generate_schema()

    app_config.route_handlers = [*app_config.route_handlers, asyncapi_schema]
    return app_config
```

### Add Middleware via Plugin

```python
def on_app_init(self, app_config: AppConfig) -> AppConfig:
    app_config.middleware = [*app_config.middleware, MyMiddleware]
    return app_config
```

### Access App State

```python
from litestar.datastructures import State

@get("/")
async def handler(state: State) -> dict:
    return {"value": state.my_value}
```

## Related Files in Project

- `src/litestar_asyncapi/plugin.py` - Main plugin
- `src/litestar_asyncapi/config.py` - Configuration
- `src/tests/conftest.py` - Test fixtures
- `src/tests/test_plugin.py` - Plugin tests
