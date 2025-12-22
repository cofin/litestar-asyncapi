# AsyncAPI Plugin Research & Analysis

**Document Version**: 1.0
**Date**: 2025-12-17
**Complexity Assessment**: Complex (10+ checkpoints)
**Status**: Research Complete

---

## Executive Summary

This research document provides comprehensive analysis for implementing AsyncAPI 3.0 support in the litestar-asyncapi plugin. The analysis covers existing ASGI implementations, Litestar's internal OpenAPI architecture, the full AsyncAPI 3.0 specification, and a recommended incremental implementation strategy.

The recommended approach mirrors Litestar's existing OpenAPI patterns for consistency and maintainability, while targeting 100% AsyncAPI 3.0.0 specification compliance.

---

## 1. Existing AsyncAPI Implementations Analysis

### 1.1 FastStream (Best-in-Class Reference)

FastStream is the most mature Python framework for AsyncAPI documentation generation. Key architectural insights:

**Source**: [FastStream GitHub](https://github.com/ag2ai/faststream)

**Key Features**:
- Automatic AsyncAPI documentation generation from decorated handlers
- Unified API across Kafka, RabbitMQ, NATS, and Redis
- Built-in Pydantic validation for message serialization
- Zero-configuration documentation that "won't cost anything"
- CLI command for serving docs: `faststream docs serve app:application`

**Architecture Pattern**:
- Decorator-based handler registration (`@broker.subscriber()`, `@broker.publisher()`)
- Type introspection for schema generation from Pydantic models
- Runtime extraction of channels and operations from decorated functions
- Automatic inference of message formats from type hints

**What We Can Learn**:
1. Automatic discovery is preferred over manual configuration
2. Decorators provide a clean API for metadata annotation
3. CLI tooling enhances developer experience
4. Type hints are the primary source of schema information

### 1.2 asyncapi-python (dutradda)

**Source**: [asyncapi-python Documentation](https://dutradda.github.io/asyncapi-python/)

**Limitations**:
- Only supports AsyncAPI 2.0.0 (not 3.0)
- Focuses on specification translation rather than auto-generation
- Limited protocol support (kafka, redis, postgres via broadcaster)
- No WebSocket binding support

**Useful Patterns**:
- `AutoSpec` class for decorator-based specification
- `build_api()` function for building from YAML
- Documentation serving via HTTP endpoint

### 1.3 Gap Analysis: No Existing Litestar/ASGI Implementation

After extensive research, no existing AsyncAPI implementation targets:
- Litestar framework specifically
- ASGI WebSocket handler introspection
- AsyncAPI 3.0 specification compliance

This creates an opportunity for litestar-asyncapi to become the reference implementation for ASGI AsyncAPI documentation.

---

## 2. Litestar OpenAPI Architecture Analysis

### 2.1 Module Structure

The Litestar OpenAPI implementation follows a well-organized architecture:

```
litestar/openapi/
├── __init__.py           # Public exports
├── config.py             # OpenAPIConfig dataclass
├── controller.py         # Route handler (legacy)
├── datastructures.py     # Helper data structures
├── plugins.py            # Render plugins (JSON, YAML, UI)
└── spec/                 # OpenAPI specification objects (~30 files)
    ├── __init__.py
    ├── base.py           # BaseSchemaObject with serialization
    ├── open_api.py       # Root OpenAPI object
    ├── info.py           # Info, Contact, License
    ├── server.py         # Server, ServerVariable
    ├── paths.py          # Paths collection
    ├── path_item.py      # Individual path
    ├── operation.py      # HTTP operation
    ├── parameter.py      # Parameters
    ├── request_body.py   # Request bodies
    ├── response.py       # Responses
    ├── schema.py         # JSON Schema
    ├── components.py     # Reusable components
    ├── security_scheme.py # Security definitions
    └── [additional spec objects...]

litestar/_openapi/
├── __init__.py
├── datastructures.py     # OpenAPIContext, SchemaRegistry
├── parameters.py         # Parameter extraction
├── path_item.py          # Path item generation
├── plugin.py             # Internal plugin logic
├── request_body.py       # Request body extraction
├── responses.py          # Response extraction
├── utils.py              # Utilities
└── schema_generation/    # Schema generation logic
    ├── __init__.py
    ├── schema.py         # Main SchemaGenerator class
    ├── constrained_fields.py
    ├── examples.py
    ├── utils.py
    └── plugins/          # Type-specific plugins
        ├── dataclass.py
        ├── pagination.py
        ├── struct.py
        └── typed_dict.py
```

### 2.2 Key Patterns from OpenAPI Implementation

**OpenAPIConfig Pattern** (`config.py`):
```python
@dataclass
class OpenAPIConfig:
    title: str
    version: str
    description: str | None = None
    servers: list[Server] = field(default_factory=lambda: [Server(url="/")])
    components: Components | list[Components] = field(default_factory=Components)
    render_plugins: Sequence[OpenAPIRenderPlugin] = field(default=(ScalarRenderPlugin(),))
    path: str = "/schema"
    # ... additional configuration

    def to_openapi_schema(self) -> OpenAPI:
        """Convert config to OpenAPI root object."""
        return OpenAPI(info=Info(...), ...)
```

**Render Plugin Pattern** (`plugins.py`):
```python
class OpenAPIRenderPlugin(ABC):
    paths: list[str]

    def __init__(self, *, path: str | Sequence[str], media_type: MediaType, ...):
        self.paths = [path] if isinstance(path, str) else list(path)

    @abstractmethod
    def render(self, request: Request, openapi_schema: dict[str, Any]) -> bytes:
        raise NotImplementedError

    @staticmethod
    def get_openapi_json_route(request: Request) -> str:
        return request.app.route_reverse(OPENAPI_JSON_HANDLER_NAME)
```

**Spec Object Pattern** (`spec/base.py`):
```python
@dataclass
class BaseSchemaObject:
    """Base for all OpenAPI spec objects with serialization support."""

    def to_schema(self) -> dict[str, Any]:
        """Serialize to dict for JSON/YAML output."""
        ...
```

### 2.3 Schema Generation Architecture

The `_openapi/schema_generation/schema.py` module provides:

1. **TYPE_MAP**: Mapping Python types to OpenAPI Schema objects
2. **SchemaGenerator class**: Orchestrates type conversion
3. **SchemaRegistry**: Caches generated schemas for $ref reuse
4. **Plugin support**: Extensible for Pydantic, dataclass, msgspec, TypedDict

Key method signatures:
```python
class SchemaGenerator:
    def __init__(self, context: OpenAPIContext):
        self.context = context
        self.registry = SchemaRegistry()

    def generate_schema(self, field_definition: FieldDefinition) -> Schema | Reference:
        """Generate schema for a type annotation."""
        ...

    def process_field_definition(self, field: FieldDefinition) -> Schema:
        """Process field metadata into schema properties."""
        ...
```

---

## 3. AsyncAPI 3.0 Specification Analysis

### 3.1 Root Structure

The AsyncAPI 3.0.0 specification defines these root-level objects:

```yaml
asyncapi: "3.0.0"           # Required: Version
id: "urn:example:app"       # Optional: Application identifier
info:                       # Required: API metadata
  title: "My API"
  version: "1.0.0"
defaultContentType: "application/json"
servers: {}                 # Server definitions
channels: {}                # Channel definitions
operations: {}              # Operation definitions
components: {}              # Reusable components
```

### 3.2 Key Object Definitions

**Info Object** (Required fields: title, version):
- title, version, description
- termsOfService, contact, license
- tags, externalDocs

**Server Object** (Required: host, protocol):
- host: "localhost:8080"
- protocol: "ws" | "wss" | "kafka" | "amqp" | ...
- protocolVersion, pathname, description
- variables: ServerVariable objects
- security, tags, bindings

**Channel Object**:
- address: "/chat/{room}" (supports parameters)
- messages: dict of Message objects
- title, summary, description
- servers: list of server references
- parameters: dict of Parameter objects
- tags, externalDocs, bindings

**Operation Object** (Required: action, channel):
- action: "send" | "receive"
- channel: Reference to Channel
- title, summary, description
- security, tags, bindings
- traits: list of OperationTrait
- messages: list of Message references
- reply: ReplyObject (for request-reply patterns)

**Message Object**:
- headers: Schema for message headers
- payload: Schema for message body
- correlationId: CorrelationId object
- contentType: MIME type
- name, title, summary, description
- tags, externalDocs, bindings
- examples: list of MessageExample
- traits: list of MessageTrait

**Components Object** (Reusable definitions):
- schemas, servers, channels, operations
- messages, securitySchemes, parameters
- correlationIds, replies
- operationTraits, messageTraits
- serverBindings, channelBindings, operationBindings, messageBindings

### 3.3 WebSocket Binding Specification

The WebSocket binding is particularly relevant for Litestar integration:

**Server Binding**:
```yaml
servers:
  production:
    host: example.com
    protocol: ws
    bindings:
      ws:
        headers:
          type: object
          properties:
            Authorization:
              type: string
        query:
          type: object
          properties:
            token:
              type: string
```

**Channel Binding**:
```yaml
channels:
  chat:
    bindings:
      ws:
        method: GET  # HTTP method for WebSocket upgrade
        query:
          type: object
          properties:
            room:
              type: string
        headers:
          type: object
          properties:
            X-Custom-Header:
              type: string
```

**Operation Binding**: No WebSocket-specific operation binding defined.

**Message Binding**:
```yaml
messages:
  chatMessage:
    bindings:
      ws:
        # No specific fields defined for WebSocket message binding
```

### 3.4 Key Differences from OpenAPI

| Aspect | OpenAPI | AsyncAPI |
|--------|---------|----------|
| Primary focus | Request-response HTTP | Event-driven messaging |
| Root object | paths | channels + operations |
| Actions | HTTP methods (GET, POST) | send/receive |
| Direction | Server responds to client | Bidirectional |
| Transport | HTTP/HTTPS | WebSocket, Kafka, AMQP, etc. |
| Schema version | 3.1.x | 3.0.0 |

---

## 4. Litestar WebSocket & Channels Integration Points

### 4.1 WebsocketRouteHandler

Located at `litestar/handlers/websocket_handlers/route_handler.py`:

```python
class WebsocketRouteHandler(BaseRouteHandler):
    __slots__ = ("_kwargs_model", "_websocket_class")

    def __init__(
        self,
        path: str | list[str] | None = None,
        *,
        fn: AsyncAnyCallable,
        dependencies: Dependencies | None = None,
        guards: Sequence[Guard] | None = None,
        middleware: Sequence[Middleware] | None = None,
        name: str | None = None,
        parameters: ParametersMap | None = None,
        websocket_class: type[WebSocket] | None = None,
        **kwargs: Any,
    ):
        ...
```

**Extraction Points for AsyncAPI**:
- `path` → Channel address
- `fn` signature → Message schemas (from type hints)
- `parameters` → Channel parameters
- `name` → Operation identifier
- Handler body analysis → send/receive operations

### 4.2 ChannelsPlugin

Located at `litestar/channels/plugin.py`:

```python
class ChannelsPlugin(InitPlugin, AbstractAsyncContextManager):
    def __init__(
        self,
        backend: ChannelsBackend,
        *,
        channels: Iterable[str] | None = None,
        arbitrary_channels_allowed: bool = False,
        create_ws_route_handlers: bool = False,
        ws_handler_base_path: str = "/",
        ws_send_mode: WebSocketMode = "text",
        ...
    ):
        ...

    def publish(self, data: LitestarEncodableType, channels: str | Iterable[str]) -> None:
        """Publish data to channels."""
        ...

    async def subscribe(self, channels: str | Iterable[str], history: int | None = None) -> Subscriber:
        """Subscribe to channels."""
        ...
```

**Extraction Points for AsyncAPI**:
- `channels` → Channel definitions
- `backend` type → Server protocol hints
- `ws_handler_base_path` + channel names → Channel addresses
- `publish()` calls → send operations
- `subscribe()` calls → receive operations

### 4.3 Mapping Strategy

| Litestar Source | AsyncAPI Target |
|-----------------|-----------------|
| `@websocket("/path")` | Channel with address "/path" |
| `WebsocketRouteHandler.path` | Channel.address |
| Handler parameters | Channel.parameters |
| `socket.receive_*()` | Operation(action="receive") |
| `socket.send_*()` | Operation(action="send") |
| Type hints on receive | Message.payload (for client→server) |
| Type hints on send | Message.payload (for server→client) |
| ChannelsPlugin.channels | Additional Channel definitions |
| ChannelsPlugin.publish | Operation(action="send") |
| ChannelsPlugin.subscribe | Operation(action="receive") |

---

## 5. Recommended Architecture

### 5.1 Directory Structure

```
src/litestar_asyncapi/
├── __init__.py                    # Public exports
├── config.py                      # AsyncAPIConfig dataclass
├── plugin.py                      # AsyncAPIPlugin (InitPluginProtocol)
├── spec/                          # AsyncAPI 3.0 spec objects
│   ├── __init__.py
│   ├── base.py                    # BaseSchemaObject
│   ├── asyncapi.py                # Root AsyncAPI object
│   ├── info.py                    # Info, Contact, License
│   ├── server.py                  # Server, ServerVariable
│   ├── channel.py                 # Channel, Parameter
│   ├── operation.py               # Operation, OperationTrait
│   ├── message.py                 # Message, MessageTrait, MessageExample
│   ├── schema.py                  # Multi-format schema
│   ├── components.py              # Components
│   ├── reference.py               # Reference ($ref)
│   ├── security_scheme.py         # SecurityScheme
│   ├── tag.py                     # Tag
│   ├── external_docs.py           # ExternalDocumentation
│   ├── correlation_id.py          # CorrelationId
│   ├── reply.py                   # Reply, ReplyAddress
│   ├── enums.py                   # Enumerations
│   └── bindings/                  # Protocol bindings
│       ├── __init__.py
│       ├── base.py                # Base binding classes
│       └── websocket.py           # WebSocket bindings
├── _asyncapi/                     # Internal generation
│   ├── __init__.py
│   ├── generator.py               # Document generator
│   ├── utils.py                   # Utilities
│   ├── schema_generation/         # Schema generation
│   │   ├── __init__.py
│   │   ├── schema.py              # SchemaGenerator
│   │   └── utils.py
│   └── extractors/                # Handler extractors
│       ├── __init__.py
│       ├── websocket.py           # WebSocket handler extractor
│       └── channels.py            # ChannelsPlugin extractor
├── plugins.py                     # Render plugins
└── extensions/                    # Optional integrations
    └── __init__.py
```

### 5.2 Component Relationships

```
+------------------+
|  AsyncAPIPlugin  |
|  (InitPlugin)    |
+--------+---------+
         |
         | on_app_init()
         v
+--------+---------+     +-----------------+
|  AsyncAPIConfig  |---->|   Generator     |
+------------------+     +--------+--------+
                                  |
         +------------------------+------------------------+
         |                        |                        |
         v                        v                        v
+--------+--------+    +----------+----------+    +--------+--------+
| WebSocket       |    | ChannelsPlugin      |    | Schema          |
| Extractor       |    | Extractor           |    | Generator       |
+-----------------+    +---------------------+    +-----------------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
                    +-------------+-------------+
                    |     AsyncAPI Document     |
                    |  (spec/ objects)          |
                    +-------------+-------------+
                                  |
         +------------------------+------------------------+
         |                        |                        |
         v                        v                        v
+--------+--------+    +----------+----------+    +--------+--------+
| JSON Render     |    | YAML Render         |    | UI Render       |
| Plugin          |    | Plugin              |    | Plugin          |
+-----------------+    +---------------------+    +-----------------+
```

---

## 6. Implementation Strategy

### 6.1 Incremental PRD Phases

**Phase 1: Spec Foundation** (PRD-001)
- All AsyncAPI 3.0 spec dataclasses
- Serialization to dict/JSON/YAML
- WebSocket bindings

**Phase 2: Schema Generation** (PRD-002)
- Type → Schema converters
- Support for Pydantic, dataclass, msgspec
- SchemaRegistry for $ref

**Phase 3: Handler Discovery** (PRD-003)
- WebSocket handler extraction
- ChannelsPlugin integration
- Operation mapping (send/receive)

**Phase 4: Document Generation** (PRD-004)
- Full document assembly
- Reference resolution
- Validation

**Phase 5: Render Plugins** (PRD-005)
- JSON/YAML rendering
- UI plugin (AsyncAPI Studio)
- Route registration

**Phase 6: Advanced Features** (PRD-006)
- Traits support
- Custom decorators
- Additional bindings

### 6.2 Quality Gates

Each phase must pass:
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] 90%+ test coverage
- [ ] Pattern compliance verified
- [ ] No anti-patterns

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AsyncAPI spec updates | Low | High | Pin to 3.0.0, monitor releases |
| WebSocket patterns vary | Medium | Medium | Decorator for explicit override |
| Schema type edge cases | Medium | Medium | Comprehensive type testing |
| UI bundle size | Medium | Low | CDN option, optional dep |
| Performance on large apps | Low | Medium | Lazy eval, caching |

---

## 8. References

### Specifications
- [AsyncAPI 3.0.0 Specification](https://www.asyncapi.com/docs/reference/specification/v3.0.0)
- [JSON Schema Draft 07](https://json-schema.org/specification-links.html#draft-7)

### Implementations
- [FastStream](https://github.com/ag2ai/faststream) - AsyncAPI generation for message brokers
- [asyncapi-python](https://github.com/dutradda/asyncapi-python) - AsyncAPI 2.0 Python library

### Litestar
- [Litestar Documentation](https://docs.litestar.dev/)
- [Litestar OpenAPI Source](https://github.com/litestar-org/litestar/tree/main/litestar/openapi)
- [Litestar Channels Source](https://github.com/litestar-org/litestar/tree/main/litestar/channels)

### Tools
- [AsyncAPI Tools](https://www.asyncapi.com/tools) - Official tooling ecosystem
- [AsyncAPI Studio](https://studio.asyncapi.com/) - Visual editor and viewer

---

**Word Count**: ~2,400 words
