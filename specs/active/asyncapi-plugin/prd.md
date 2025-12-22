# Product Requirements Document: litestar-asyncapi Plugin

**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: Draft
**Complexity**: Complex
**Checkpoints**: 10+

---

## Intelligence Context

### Complexity Assessment
This is a **Complex** feature requiring 10+ checkpoints due to:
- Full AsyncAPI 3.0 specification implementation (~25 spec objects)
- Multiple integration points (WebSockets, Channels, DTOs)
- Schema generation from type annotations
- UI serving infrastructure
- Protocol bindings architecture

### Similar Features Analyzed
1. **Litestar OpenAPI** (`litestar/openapi/`) - Primary pattern reference
2. **FastStream** - AsyncAPI generation patterns
3. **asyncapi-python** - Specification handling patterns

### Patterns to Follow
- InitPluginProtocol implementation pattern
- Configuration dataclass pattern (field-level docs)
- Render plugin abstract base class pattern
- Schema generation with SchemaRegistry
- Spec objects with BaseSchemaObject serialization

---

## 1. Problem Statement

### 1.1 Background

AsyncAPI is an open-source specification for defining asynchronous/event-driven APIs, analogous to how OpenAPI defines REST APIs. While Litestar provides excellent OpenAPI support for HTTP endpoints, there is no native support for documenting WebSocket handlers and pub/sub channels using the AsyncAPI specification.

Modern applications increasingly rely on real-time, event-driven communication patterns:
- WebSocket connections for live updates
- Message broker integration (Kafka, RabbitMQ, NATS)
- Pub/sub patterns via Litestar's ChannelsPlugin

Without AsyncAPI documentation, developers face these challenges:
1. Manual documentation of WebSocket message formats
2. No machine-readable specification for code generation
3. Inconsistent documentation across teams
4. Difficulty communicating async API contracts to consumers

### 1.2 Problem Summary

Litestar applications with WebSocket handlers and pub/sub channels lack standardized, automatic documentation generation. The AsyncAPI specification provides this standard, but no implementation exists for Litestar.

### 1.3 Target Users

1. **Litestar developers** building real-time applications with WebSockets
2. **API consumers** who need to understand async message formats
3. **DevOps/Platform teams** integrating with message brokers
4. **Technical writers** documenting event-driven APIs

### 1.4 Success Metrics

- 100% AsyncAPI 3.0.0 specification compliance for implemented features
- Automatic discovery of WebSocket handlers without manual annotation
- Schema generation accuracy matching Litestar OpenAPI quality
- 90%+ test coverage across all modules
- Documentation serving with <100ms response time

---

## 2. Acceptance Criteria

### 2.1 Core Requirements

**AC-1: Specification Compliance**
- MUST generate valid AsyncAPI 3.0.0 documents
- MUST include all required fields per specification
- MUST support JSON and YAML output formats
- MUST validate generated documents against AsyncAPI schema

**AC-2: WebSocket Handler Integration**
- MUST automatically discover all `@websocket` decorated handlers
- MUST extract channel addresses from handler paths
- MUST extract path parameters as channel parameters
- MUST infer message schemas from type annotations
- MUST determine operation direction (send/receive) from handler patterns

**AC-3: ChannelsPlugin Integration**
- MUST discover channels defined in ChannelsPlugin configuration
- MUST map publish operations to send operations
- MUST map subscribe operations to receive operations
- MUST support arbitrary channel patterns when enabled

**AC-4: Schema Generation**
- MUST convert Pydantic models to AsyncAPI schemas
- MUST convert attrs classes to AsyncAPI schemas
- MUST convert dataclasses to AsyncAPI schemas
- MUST convert msgspec Struct to AsyncAPI schemas
- MUST convert TypedDict to AsyncAPI schemas
- MUST handle nested types, unions, and generics
- MUST use $ref for schema reuse

**AC-5: Configuration**
- MUST provide AsyncAPIConfig for customization
- MUST allow setting API title, version, description
- MUST allow configuring server definitions
- MUST allow custom render plugins
- MUST allow path customization for docs endpoint

**AC-6: Documentation Serving**
- MUST serve AsyncAPI JSON at configurable path
- MUST serve AsyncAPI YAML at configurable path
- MUST provide UI viewer for interactive documentation
- MUST integrate seamlessly with Litestar app lifecycle

### 2.2 Edge Cases

**EC-1: Handler Variations**
- Multiple WebSocket handlers on same path (different methods)
- Handlers with complex path parameters
- Handlers with guards and dependencies
- Handlers without explicit message types

**EC-2: Schema Variations**
- Recursive type definitions
- Generic types with type variables
- Union types with discriminators
- Optional fields with defaults
- Custom validators and constraints

**EC-3: Configuration Variations**
- Multiple AsyncAPI documents (multi-app scenario)
- Custom serialization settings
- Security scheme configurations
- External documentation links

---

## 3. Technical Approach

### 3.1 Architecture Overview

The plugin follows Litestar's established patterns, mirroring the OpenAPI implementation:

```
+-------------------+
|   AsyncAPIPlugin  |
| (InitPluginProtocol)
+--------+----------+
         |
         | on_app_init()
         v
+--------+----------+
|  AsyncAPIConfig   |
+--------+----------+
         |
         | to_asyncapi_schema()
         v
+--------+----------+
|    Generator      |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+---+---+ +---+----+
|Extract| |Schema  |
|  ors  | |Gen     |
+---+---+ +---+----+
    |         |
    +----+----+
         |
         v
+--------+----------+
| AsyncAPI Document |
| (spec/ objects)   |
+--------+----------+
         |
    +----+----+
    |    |    |
    v    v    v
  JSON YAML  UI
```

### 3.2 Module Organization

```
src/litestar_asyncapi/
├── __init__.py                 # Public API exports
├── config.py                   # AsyncAPIConfig dataclass
├── plugin.py                   # AsyncAPIPlugin implementation
├── plugins.py                  # Render plugins
├── spec/                       # AsyncAPI 3.0 spec objects
│   ├── __init__.py
│   ├── base.py                 # BaseSchemaObject
│   ├── asyncapi.py             # AsyncAPI root object
│   ├── info.py                 # Info, Contact, License
│   ├── server.py               # Server, ServerVariable
│   ├── channel.py              # Channel, Parameter
│   ├── operation.py            # Operation, OperationTrait
│   ├── message.py              # Message, MessageTrait
│   ├── schema.py               # Multi-format Schema
│   ├── components.py           # Components
│   ├── reference.py            # Reference
│   ├── security_scheme.py      # SecurityScheme
│   ├── tag.py                  # Tag
│   ├── external_docs.py        # ExternalDocumentation
│   ├── correlation_id.py       # CorrelationId
│   ├── reply.py                # Reply, ReplyAddress
│   ├── enums.py                # Enumerations
│   └── bindings/               # Protocol bindings
│       ├── __init__.py
│       ├── base.py
│       └── websocket.py
├── _asyncapi/                  # Internal generation
│   ├── __init__.py
│   ├── generator.py            # Document generator
│   ├── utils.py
│   ├── schema_generation/      # Schema generation
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── utils.py
│   └── extractors/             # Handler extractors
│       ├── __init__.py
│       ├── websocket.py
│       └── channels.py
└── extensions/                 # Optional integrations
    └── __init__.py
```

### 3.3 Key Components

#### 3.3.1 AsyncAPIConfig

```python
@dataclass
class AsyncAPIConfig:
    """Configuration for AsyncAPI documentation generation.

    Attributes documented inline below each field.
    """

    title: str
    """Title of the AsyncAPI document."""
    version: str
    """API version string (e.g., '1.0.0')."""
    description: str | None = None
    """Optional API description (supports Markdown)."""
    servers: dict[str, Server] = field(default_factory=dict)
    """Server definitions keyed by name."""
    default_content_type: str = "application/json"
    """Default content type for messages."""
    id: str | None = None
    """Optional application identifier (URI)."""
    terms_of_service: str | None = None
    """URL to terms of service."""
    contact: Contact | None = None
    """Contact information."""
    license: License | None = None
    """License information."""
    tags: list[Tag] | None = None
    """List of tags for grouping."""
    external_docs: ExternalDocumentation | None = None
    """External documentation link."""
    components: Components | None = None
    """Predefined reusable components."""
    path: str = "/asyncapi"
    """Base path for documentation endpoints."""
    render_plugins: Sequence[AsyncAPIRenderPlugin] = field(
        default_factory=lambda: (JsonRenderPlugin(), YamlRenderPlugin())
    )
    """Plugins for rendering documentation."""
    include_websockets: bool = True
    """Auto-discover WebSocket handlers."""
    include_channels: bool = True
    """Auto-discover ChannelsPlugin channels."""

    def to_asyncapi_schema(self) -> AsyncAPI:
        """Convert configuration to AsyncAPI root object."""
        ...
```

#### 3.3.2 AsyncAPIPlugin

```python
class AsyncAPIPlugin(InitPluginProtocol):
    """AsyncAPI documentation plugin for Litestar.

    Automatically generates AsyncAPI 3.0 documentation from
    WebSocket handlers and ChannelsPlugin configuration.
    """

    __slots__ = ("_config", "_schema", "_generator")

    def __init__(self, config: AsyncAPIConfig | None = None) -> None:
        self._config = config or AsyncAPIConfig(title="API", version="1.0.0")
        self._schema: AsyncAPI | None = None
        self._generator: Generator | None = None

    @property
    def config(self) -> AsyncAPIConfig:
        return self._config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Initialize plugin during app startup."""
        # Register route handlers for documentation
        # Initialize generator with app context
        return app_config

    def generate_schema(self, app: Litestar) -> AsyncAPI:
        """Generate AsyncAPI schema from application."""
        ...
```

#### 3.3.3 Spec Objects Pattern

All specification objects inherit from BaseSchemaObject:

```python
@dataclass
class BaseSchemaObject:
    """Base class for AsyncAPI specification objects."""

    def to_schema(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON/YAML output."""
        result = {}
        for field_info in fields(self):
            value = getattr(self, field_info.name)
            if value is not None and value != field_info.default:
                key = self._to_camel_case(field_info.name)
                result[key] = self._serialize_value(value)
        return result

    @staticmethod
    def _to_camel_case(name: str) -> str:
        """Convert snake_case to camelCase."""
        ...

    def _serialize_value(self, value: Any) -> Any:
        """Recursively serialize values."""
        ...
```

#### 3.3.4 Render Plugins

```python
class AsyncAPIRenderPlugin(ABC):
    """Base class for AsyncAPI render plugins."""

    paths: list[str]

    def __init__(
        self,
        *,
        path: str | Sequence[str],
        media_type: MediaType = MediaType.JSON,
    ) -> None:
        self.paths = [path] if isinstance(path, str) else list(path)
        self.media_type = media_type

    @abstractmethod
    def render(self, request: Request, schema: dict[str, Any]) -> bytes:
        """Render the AsyncAPI schema."""
        ...


class JsonRenderPlugin(AsyncAPIRenderPlugin):
    """Render AsyncAPI as JSON."""

    def __init__(self, path: str = "/asyncapi.json") -> None:
        super().__init__(path=path, media_type=MediaType.JSON)

    def render(self, request: Request, schema: dict[str, Any]) -> bytes:
        return encode_json(schema)


class YamlRenderPlugin(AsyncAPIRenderPlugin):
    """Render AsyncAPI as YAML."""

    def __init__(self, path: str = "/asyncapi.yaml") -> None:
        super().__init__(path=path, media_type=MediaType.TEXT)

    def render(self, request: Request, schema: dict[str, Any]) -> bytes:
        import yaml
        return yaml.dump(schema, default_flow_style=False).encode()


class AsyncAPIStudioPlugin(AsyncAPIRenderPlugin):
    """Render AsyncAPI documentation using AsyncAPI Studio."""

    def __init__(self, path: str = "/") -> None:
        super().__init__(path=path, media_type=MediaType.HTML)

    def render(self, request: Request, schema: dict[str, Any]) -> bytes:
        html = self._generate_studio_html(schema)
        return html.encode()
```

### 3.4 Integration Points

#### 3.4.1 WebSocket Handler Extraction

```python
class WebSocketExtractor:
    """Extract AsyncAPI channels from WebSocket handlers."""

    def extract_channels(self, app: Litestar) -> dict[str, Channel]:
        """Find all WebSocket handlers and convert to channels."""
        channels = {}
        for route in app.routes:
            if isinstance(route, WebSocketRoute):
                channel = self._route_to_channel(route)
                channels[self._generate_channel_id(route)] = channel
        return channels

    def _route_to_channel(self, route: WebSocketRoute) -> Channel:
        """Convert a WebSocket route to AsyncAPI channel."""
        handler = route.route_handler
        return Channel(
            address=route.path,
            messages=self._extract_messages(handler),
            parameters=self._extract_parameters(route),
            bindings=ChannelBindings(ws=WebSocketChannelBinding()),
        )

    def _extract_messages(self, handler: WebsocketRouteHandler) -> dict[str, Message]:
        """Extract message definitions from handler signature."""
        ...

    def _extract_parameters(self, route: WebSocketRoute) -> dict[str, Parameter]:
        """Extract path parameters."""
        ...
```

#### 3.4.2 ChannelsPlugin Extraction

```python
class ChannelsPluginExtractor:
    """Extract AsyncAPI channels from ChannelsPlugin."""

    def extract_channels(self, plugin: ChannelsPlugin) -> dict[str, Channel]:
        """Convert ChannelsPlugin channels to AsyncAPI channels."""
        channels = {}
        for channel_name in plugin._channels:
            channel = Channel(
                address=f"{plugin._handler_root_path}{channel_name}",
                title=channel_name,
            )
            channels[channel_name] = channel
        return channels

    def extract_operations(self, plugin: ChannelsPlugin) -> dict[str, Operation]:
        """Generate operations for publish/subscribe patterns."""
        ...
```

### 3.5 Schema Generation Strategy

The schema generation reuses patterns from Litestar's OpenAPI implementation:

```python
TYPE_MAP: dict[type[Any], Schema] = {
    str: Schema(type="string"),
    int: Schema(type="integer"),
    float: Schema(type="number"),
    bool: Schema(type="boolean"),
    bytes: Schema(type="string", format="binary"),
    datetime: Schema(type="string", format="date-time"),
    date: Schema(type="string", format="date"),
    UUID: Schema(type="string", format="uuid"),
    # ... additional mappings
}


class AsyncAPISchemaGenerator:
    """Generate AsyncAPI schemas from Python types."""

    def __init__(self, context: AsyncAPIContext) -> None:
        self.context = context
        self.registry = SchemaRegistry()

    def generate(self, field_definition: FieldDefinition) -> Schema | Reference:
        """Generate schema for a type."""
        if cached := self.registry.get(field_definition):
            return Reference(ref=f"#/components/schemas/{cached.name}")

        schema = self._type_to_schema(field_definition)
        self.registry.register(field_definition, schema)
        return schema

    def _type_to_schema(self, field: FieldDefinition) -> Schema:
        """Convert Python type to AsyncAPI schema."""
        ...
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Spec Objects** (`tests/unit/spec/`):
- Test each spec object serialization
- Test camelCase conversion
- Test default value handling
- Test nested object serialization

**Schema Generation** (`tests/unit/schema_generation/`):
- Test each type mapping
- Test nested types
- Test union types
- Test generic types
- Test Pydantic/dataclass/msgspec

**Extractors** (`tests/unit/extractors/`):
- Test WebSocket handler extraction
- Test ChannelsPlugin extraction
- Test operation direction inference
- Test parameter extraction

### 4.2 Integration Tests

**Full Pipeline** (`tests/integration/`):
- Test complete schema generation from app
- Test route registration
- Test JSON/YAML output
- Test UI rendering

**Example Applications**:
```python
def test_websocket_chat_app() -> None:
    """Test AsyncAPI generation for chat application."""
    @websocket("/chat/{room}")
    async def chat_handler(socket: WebSocket, room: str) -> None:
        async for message in socket.iter_json():
            await socket.send_json({"echo": message})

    app = Litestar(
        route_handlers=[chat_handler],
        plugins=[AsyncAPIPlugin(config=AsyncAPIConfig(
            title="Chat API",
            version="1.0.0"
        ))]
    )

    with TestClient(app) as client:
        response = client.get("/asyncapi/asyncapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["asyncapi"] == "3.0.0"
        assert "chat" in schema["channels"]
```

### 4.3 Coverage Requirements

| Module | Target Coverage |
|--------|-----------------|
| `spec/` | 95% |
| `_asyncapi/` | 90% |
| `plugins.py` | 90% |
| `config.py` | 95% |
| `plugin.py` | 90% |
| **Overall** | **90%+** |

---

## 5. File Changes

### 5.1 Files to Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `spec/__init__.py` | Spec exports | 50 |
| `spec/base.py` | BaseSchemaObject | 100 |
| `spec/asyncapi.py` | Root object | 80 |
| `spec/info.py` | Info, Contact, License | 120 |
| `spec/server.py` | Server, ServerVariable | 100 |
| `spec/channel.py` | Channel, Parameter | 120 |
| `spec/operation.py` | Operation, traits | 150 |
| `spec/message.py` | Message, traits | 180 |
| `spec/schema.py` | Schema object | 200 |
| `spec/components.py` | Components | 100 |
| `spec/reference.py` | Reference | 40 |
| `spec/security_scheme.py` | SecurityScheme | 120 |
| `spec/tag.py` | Tag | 50 |
| `spec/external_docs.py` | ExternalDocs | 40 |
| `spec/correlation_id.py` | CorrelationId | 50 |
| `spec/reply.py` | Reply, ReplyAddress | 80 |
| `spec/enums.py` | Enumerations | 80 |
| `spec/bindings/__init__.py` | Bindings exports | 20 |
| `spec/bindings/base.py` | Base bindings | 60 |
| `spec/bindings/websocket.py` | WebSocket bindings | 100 |
| `_asyncapi/__init__.py` | Internal exports | 20 |
| `_asyncapi/generator.py` | Document generator | 250 |
| `_asyncapi/utils.py` | Utilities | 100 |
| `_asyncapi/schema_generation/__init__.py` | Schema exports | 20 |
| `_asyncapi/schema_generation/schema.py` | SchemaGenerator | 300 |
| `_asyncapi/schema_generation/utils.py` | Schema utilities | 100 |
| `_asyncapi/extractors/__init__.py` | Extractor exports | 20 |
| `_asyncapi/extractors/websocket.py` | WebSocket extractor | 200 |
| `_asyncapi/extractors/channels.py` | Channels extractor | 150 |
| `plugins.py` | Render plugins | 250 |
| Tests (multiple files) | Test coverage | 1500+ |

**Total Estimated New Lines**: ~4,500

### 5.2 Files to Modify

| File | Changes |
|------|---------|
| `config.py` | Expand AsyncAPIConfig with all options |
| `plugin.py` | Implement full on_app_init logic |
| `__init__.py` | Export new public APIs |

---

## 6. Incremental Delivery Plan

This PRD will be implemented through 6 sequential sub-PRDs:

### PRD-001: AsyncAPI Spec Foundation
- Docs: `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md`
- All spec/ dataclasses
- Serialization support
- WebSocket bindings

### PRD-002: Schema Generation
- Docs: `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/prd.md`
- Type → Schema converters
- SchemaRegistry
- Plugin architecture

### PRD-003: Handler Discovery
- Docs: `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md`
- WebSocket extractor
- ChannelsPlugin extractor
- Operation mapping

### PRD-004: Document Generation
- Docs: `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md`
- Generator orchestration
- Reference resolution
- Validation

### PRD-005: Render Plugins
- Docs: `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/prd.md`
- JSON/YAML plugins
- UI plugin
- Route registration

### PRD-006: Advanced Features
- Docs: `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/prd.md`
- Traits support
- Custom decorators
- Additional bindings

---

## 7. Dependencies & Constraints

### 7.1 Runtime Dependencies
- `litestar>=2.0.0` (peer dependency)
- `pyyaml>=6.0` (optional, for YAML output)

### 7.2 Development Dependencies
- `pytest>=7.0`
- `pytest-anyio`
- `polyfactory` (for example generation)

### 7.3 Constraints
- Python 3.9+ support required
- AsyncAPI 3.0.0 only (no 2.x support)
- WebSocket binding is primary focus
- Must follow Litestar coding standards

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AsyncAPI 3.0 spec changes | Low | High | Pin to 3.0.0, monitor releases |
| WebSocket handler patterns vary | Medium | Medium | Decorator for explicit override |
| Schema type edge cases | Medium | Medium | Comprehensive type testing |
| UI bundle size concerns | Medium | Low | CDN option, optional dependency |
| Performance on large apps | Low | Medium | Lazy evaluation, caching |

---

## 9. Future Considerations

### 9.1 Version 2.0 Candidates
- Kafka binding support
- AMQP binding support
- MQTT binding support
- NATS binding support
- Code generation from AsyncAPI specs
- Validation middleware for incoming messages

### 9.2 Integration Opportunities
- AsyncAPI CLI integration
- AsyncAPI Studio embedding
- OpenTelemetry trace correlation

---

## 10. Detailed Technical Specifications

### 10.1 AsyncAPI 3.0 Object Model

The AsyncAPI 3.0 specification defines a hierarchical object model. Our implementation will create Python dataclasses for each object type, ensuring full type safety and IDE support.

**Root AsyncAPI Object Fields**:
- `asyncapi` (required): Version string, always "3.0.0"
- `id`: Application identifier in URI format
- `info` (required): API metadata object
- `servers`: Dictionary of server definitions
- `defaultContentType`: Default message encoding (e.g., "application/json")
- `channels`: Dictionary of channel definitions
- `operations`: Dictionary of operation definitions
- `components`: Reusable schema components

**Info Object Fields**:
- `title` (required): Human-readable API name
- `version` (required): API version string
- `description`: Markdown-formatted description
- `termsOfService`: URL to terms of service
- `contact`: Contact object with name, URL, email
- `license`: License object with name and URL
- `tags`: List of tag objects for grouping
- `externalDocs`: External documentation reference

**Server Object Fields**:
- `host` (required): Server hostname and optional port
- `protocol` (required): Protocol identifier (ws, wss, kafka, amqp, etc.)
- `protocolVersion`: Version of the protocol
- `pathname`: Path on the server (supports variables)
- `description`: Server description
- `variables`: Dictionary of server variables
- `security`: List of security requirements
- `tags`: List of tags
- `bindings`: Protocol-specific bindings

**Channel Object Fields**:
- `address`: Channel address pattern (supports parameters like `{userId}`)
- `messages`: Dictionary of message objects
- `title`: Human-readable channel name
- `summary`: Brief channel description
- `description`: Detailed description
- `servers`: List of server references
- `parameters`: Dictionary of parameter objects
- `tags`: List of tags
- `externalDocs`: External documentation
- `bindings`: Protocol-specific bindings

**Operation Object Fields**:
- `action` (required): Either "send" or "receive"
- `channel` (required): Reference to a channel
- `title`: Operation name
- `summary`: Brief description
- `description`: Detailed description
- `security`: Security requirements
- `tags`: List of tags
- `bindings`: Protocol-specific bindings
- `traits`: List of operation traits
- `messages`: List of message references
- `reply`: Reply pattern definition

**Message Object Fields**:
- `headers`: Schema for message headers
- `payload`: Schema for message payload
- `correlationId`: Correlation ID specification
- `contentType`: MIME type for encoding
- `name`: Machine-readable identifier
- `title`: Human-readable name
- `summary`: Brief description
- `description`: Detailed description
- `tags`: List of tags
- `externalDocs`: External documentation
- `bindings`: Protocol-specific bindings
- `examples`: List of example messages
- `traits`: List of message traits

### 10.2 WebSocket Binding Specifications

The WebSocket binding defines protocol-specific configurations for WebSocket communication.

**Server Binding**:
```yaml
servers:
  websocket:
    host: api.example.com
    protocol: ws
    bindings:
      ws:
        headers:
          type: object
          properties:
            Authorization:
              type: string
              description: Bearer token
        query:
          type: object
          properties:
            version:
              type: string
              description: API version
```

**Channel Binding**:
```yaml
channels:
  userEvents:
    bindings:
      ws:
        method: GET
        query:
          type: object
          properties:
            userId:
              type: string
        headers:
          type: object
          properties:
            X-Request-ID:
              type: string
```

**Message Binding**:
The WebSocket message binding does not define specific fields beyond the base message structure, as WebSocket messages are typically serialized JSON or binary data.

### 10.3 Operation Direction Inference Algorithm

Determining whether a handler performs "send" or "receive" operations requires analysis of the handler's implementation patterns:

**Heuristics for WebSocket Handlers**:

1. **Receive Operation** (client sends to server):
   - Handler calls `websocket.receive_text()`, `receive_json()`, `receive_bytes()`
   - Handler uses `async for message in websocket.iter_*()`
   - Handler awaits data from the socket

2. **Send Operation** (server sends to client):
   - Handler calls `websocket.send_text()`, `send_json()`, `send_bytes()`
   - Handler writes data to the socket

3. **Bidirectional Channels**:
   - When both patterns detected, generate both operations
   - Link operations to same channel with different message types

**Heuristics for ChannelsPlugin**:

1. **Publish** (application sends):
   - Maps to AsyncAPI "send" operation
   - Application is the sender

2. **Subscribe** (application receives):
   - Maps to AsyncAPI "receive" operation
   - Application is the receiver

**Fallback Behavior**:
When direction cannot be inferred automatically, the system will:
1. Default to bidirectional (both send and receive)
2. Allow override via decorator: `@asyncapi_operation(action="send")`
3. Log a warning suggesting explicit configuration

### 10.4 Schema Registry Implementation

The SchemaRegistry ensures efficient schema reuse and proper $ref generation:

```python
class SchemaRegistry:
    """Registry for AsyncAPI schemas with $ref support."""

    __slots__ = ("_schemas", "_name_counter")

    def __init__(self) -> None:
        self._schemas: dict[int, tuple[str, Schema]] = {}
        self._name_counter: dict[str, int] = defaultdict(int)

    def get_or_create(self, field: FieldDefinition) -> Schema | Reference:
        """Get existing schema or create and register new one."""
        key = self._compute_key(field)
        if key in self._schemas:
            name, _ = self._schemas[key]
            return Reference(ref=f"#/components/schemas/{name}")

        schema = self._generate_schema(field)
        name = self._generate_name(field)
        self._schemas[key] = (name, schema)
        return schema

    def get_components(self) -> dict[str, Schema]:
        """Get all registered schemas for components section."""
        return {name: schema for name, schema in self._schemas.values()}

    def _compute_key(self, field: FieldDefinition) -> int:
        """Compute unique key for type definition."""
        return hash((field.annotation, tuple(field.inner_types or ())))

    def _generate_name(self, field: FieldDefinition) -> str:
        """Generate unique schema name."""
        base_name = getattr(field.annotation, "__name__", str(field.annotation))
        self._name_counter[base_name] += 1
        count = self._name_counter[base_name]
        return base_name if count == 1 else f"{base_name}{count}"
```

---

## 11. Glossary

| Term | Definition |
|------|------------|
| AsyncAPI | Open-source specification for event-driven APIs |
| Channel | Named communication pathway in AsyncAPI |
| Operation | Action (send/receive) on a channel |
| Message | Data structure transmitted via channel |
| Binding | Protocol-specific configuration |
| Schema | JSON Schema defining data structure |
| Components | Reusable specification definitions |

---

**Word Count**: ~3,400 words

---

## Approval

- [ ] Technical Lead Review
- [ ] Architecture Review
- [ ] User Ready for Implementation
