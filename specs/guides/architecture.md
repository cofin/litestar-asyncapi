# litestar-asyncapi Architecture Guide

## Overview

**litestar-asyncapi** is an official Litestar plugin that provides AsyncAPI support for event-driven/asynchronous APIs (WebSockets, message brokers, etc.). It mirrors how OpenAPI documents REST APIs but is designed for async messaging patterns.

## Core Architecture

### Plugin Pattern

The plugin follows Litestar's standard plugin architecture:

```
litestar.plugins.InitPluginProtocol
           │
           ▼
    AsyncAPIPlugin
           │
           ├── on_app_init() - Lifecycle hook
           │
           └── config: AsyncAPIConfig - Plugin configuration
```

### Current Components

```
src/litestar_asyncapi/
├── __init__.py      # Public exports (AsyncAPIConfig, AsyncAPIPlugin)
├── config.py        # AsyncAPIConfig dataclass
├── plugin.py        # AsyncAPIPlugin (InitPluginProtocol)
└── py.typed         # PEP 561 marker
```

### Planned Components (Roadmap)

```
src/litestar_asyncapi/
├── __init__.py
├── config.py
├── plugin.py
├── py.typed
├── schema/                    # AsyncAPI schema generation
│   ├── __init__.py
│   ├── generator.py          # Main schema generator
│   ├── channels.py           # Channel definitions
│   ├── messages.py           # Message schemas
│   └── components.py         # Reusable components
├── handlers/                  # Route handlers for docs
│   ├── __init__.py
│   ├── json.py               # JSON schema endpoint
│   ├── yaml.py               # YAML schema endpoint
│   └── ui.py                 # UI render handler
├── ui/                        # Documentation UI
│   ├── __init__.py
│   ├── templates/            # HTML templates
│   └── static/               # Static assets
└── extensions/                # Framework integrations
    ├── __init__.py
    ├── websocket.py          # WebSocket channel extraction
    └── channels.py           # Litestar channels integration
```

## AsyncAPI Specification Concepts

### Key Entities

1. **Channels** - Named communication endpoints (like topics/queues)
2. **Messages** - Data format definitions
3. **Operations** - Actions on channels (publish/subscribe)
4. **Servers** - Connection information
5. **Components** - Reusable schema definitions

### Mapping to Litestar

| AsyncAPI | Litestar Equivalent |
|----------|---------------------|
| Channel | WebSocket route / Channel handler |
| Message | Pydantic model / DTO |
| Operation | Handler method |
| Server | App connection config |

## Design Principles

### 1. Non-Intrusive
- Works with existing Litestar apps without changes
- Extracts information from decorators and type hints

### 2. Automatic Discovery
- Finds WebSocket handlers automatically
- Extracts DTOs from type annotations
- Infers channel names from route paths

### 3. Extensible
- Custom extractors for different patterns
- Plugin system for additional protocols
- Template customization

### 4. Spec Compliant
- Targets AsyncAPI 3.0 specification
- Full spec compliance where applicable
- Clear documentation of limitations

## Integration Points

### Litestar Lifecycle

```python
# Plugin hooks into app initialization
def on_app_init(self, app_config: AppConfig) -> AppConfig:
    # 1. Register schema generation routes
    # 2. Set up UI serving routes
    # 3. Configure any middleware
    return app_config
```

### WebSocket Handler Extraction

```python
# From handler like:
@websocket("/chat/{room}")
async def chat_handler(socket: WebSocket, room: str) -> None:
    pass

# Extract:
# - Channel: /chat/{room}
# - Parameters: room (string)
# - Operations: subscribe/publish based on socket usage
```

### Message Schema Extraction

```python
# From DTO:
@dataclass
class ChatMessage:
    user: str
    content: str
    timestamp: datetime

# Generate AsyncAPI message schema with JSON Schema
```

## Testing Strategy

### Unit Tests
- Schema generation logic
- Configuration validation
- Individual component tests

### Integration Tests
- Full app with plugin
- Route registration
- Schema output validation

### Fixtures Pattern
```python
@pytest.fixture
def asyncapi_plugin(asyncapi_config: AsyncAPIConfig) -> AsyncAPIPlugin:
    return AsyncAPIPlugin(config=asyncapi_config)

@pytest.fixture
def app(asyncapi_plugin: AsyncAPIPlugin) -> Litestar:
    return Litestar(plugins=[asyncapi_plugin])
```

## Development Workflow

1. **PRD Phase** - Design feature with `/prd`
2. **Implementation** - Build with `/implement`
3. **Testing** - Ensure 90%+ coverage
4. **Review** - Quality gates and pattern extraction

## Dependencies

### Runtime
- `litestar>=2.0.0` - Core framework
- `sniffio` - Async library detection

### Development
- `pytest` + `pytest-anyio` - Testing
- `ruff` - Linting
- `mypy` + `pyright` - Type checking
- `slotscheck` - Slots validation
