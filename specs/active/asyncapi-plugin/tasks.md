# Task Breakdown: litestar-asyncapi Plugin

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Created**: 2025-12-17
**Total Sub-PRDs**: 6
**Sub-PRD Docs Index**: `specs/active/asyncapi-plugin/prds/README.md`

---

## Overview

This document breaks down the litestar-asyncapi implementation into 6 incremental PRDs. Each PRD is self-contained with independent tests and can be merged separately.

```
PRD-001 ──► PRD-002 ──► PRD-003 ──► PRD-004 ──► PRD-005 ──► PRD-006
  │           │           │           │           │           │
  │           │           │           │           │           │
 Spec      Schema      Handler     Document    Render     Advanced
Objects  Generation  Discovery  Generation  Plugins    Features
```

---

## PRD-001: AsyncAPI Spec Foundation

### Description
Create the complete AsyncAPI 3.0 specification object model as Python dataclasses. This forms the foundation for all subsequent phases.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/`

### Files to Create
- `src/litestar_asyncapi/spec/__init__.py`
- `src/litestar_asyncapi/spec/base.py`
- `src/litestar_asyncapi/spec/asyncapi.py`
- `src/litestar_asyncapi/spec/info.py`
- `src/litestar_asyncapi/spec/server.py`
- `src/litestar_asyncapi/spec/channel.py`
- `src/litestar_asyncapi/spec/operation.py`
- `src/litestar_asyncapi/spec/message.py`
- `src/litestar_asyncapi/spec/schema.py`
- `src/litestar_asyncapi/spec/components.py`
- `src/litestar_asyncapi/spec/reference.py`
- `src/litestar_asyncapi/spec/security_scheme.py`
- `src/litestar_asyncapi/spec/tag.py`
- `src/litestar_asyncapi/spec/external_docs.py`
- `src/litestar_asyncapi/spec/correlation_id.py`
- `src/litestar_asyncapi/spec/reply.py`
- `src/litestar_asyncapi/spec/enums.py`
- `src/litestar_asyncapi/spec/bindings/__init__.py`
- `src/litestar_asyncapi/spec/bindings/base.py`
- `src/litestar_asyncapi/spec/bindings/websocket.py`

### Tests
- `src/tests/unit/spec/test_base.py`
- `src/tests/unit/spec/test_asyncapi.py`
- `src/tests/unit/spec/test_info.py`
- `src/tests/unit/spec/test_server.py`
- `src/tests/unit/spec/test_channel.py`
- `src/tests/unit/spec/test_operation.py`
- `src/tests/unit/spec/test_message.py`
- `src/tests/unit/spec/test_schema.py`
- `src/tests/unit/spec/test_bindings.py`

### Patterns to Follow
- Mirror `litestar/openapi/spec/` structure
- BaseSchemaObject with `to_schema()` method
- `__slots__` on all classes
- PEP 604 type hints (`T | None`)
- Google-style docstrings

### Acceptance Criteria
- [ ] All spec objects serialize correctly to dict
- [ ] camelCase conversion works for JSON output
- [ ] Default values excluded from output
- [ ] Nested objects serialize recursively
- [ ] 95% test coverage for spec/

### Dependencies
None

---

## PRD-002: Schema Generation

### Description
Implement the schema generation system to convert Python types to AsyncAPI-compatible JSON Schema objects.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/`

### Files to Create
- `src/litestar_asyncapi/_asyncapi/__init__.py`
- `src/litestar_asyncapi/_asyncapi/schema_generation/__init__.py`
- `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py`
- `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
- `src/litestar_asyncapi/_asyncapi/datastructures.py`

### Tests
- `src/tests/unit/schema_generation/test_schema.py`
- `src/tests/unit/schema_generation/test_types.py`
- `src/tests/unit/schema_generation/test_pydantic.py`
- `src/tests/unit/schema_generation/test_dataclass.py`
- `src/tests/unit/schema_generation/test_msgspec.py`

### Key Components
1. **TYPE_MAP**: Python type to Schema mapping
2. **AsyncAPISchemaGenerator**: Main generator class
3. **SchemaRegistry**: $ref management and caching
4. **Plugin support**: Type-specific handlers

### Patterns to Follow
- Reference `litestar/_openapi/schema_generation/`
- Use FieldDefinition for type introspection
- Support Litestar's existing type annotation patterns

### Acceptance Criteria
- [ ] Basic types map correctly (str, int, float, bool, etc.)
- [ ] Pydantic models generate valid schemas
- [ ] attrs classes generate valid schemas
- [ ] Dataclasses generate valid schemas
- [ ] msgspec Struct generates valid schemas
- [ ] Nested types handled correctly
- [ ] Union types generate oneOf schemas
- [ ] Generic types resolve correctly
- [ ] $ref used for repeated schemas
- [ ] 90% test coverage

### Dependencies
- PRD-001 (spec objects)

---

## PRD-003: Handler Discovery

### Description
Implement extractors to discover WebSocket handlers and ChannelsPlugin configurations, converting them to AsyncAPI channels and operations.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/`

### Files to Create
- `src/litestar_asyncapi/_asyncapi/extractors/__init__.py`
- `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- `src/litestar_asyncapi/_asyncapi/extractors/channels.py`
- `src/litestar_asyncapi/_asyncapi/utils.py`

### Tests
- `src/tests/unit/extractors/test_websocket.py`
- `src/tests/unit/extractors/test_channels.py`
- `src/tests/integration/test_discovery.py`

### Key Components
1. **WebSocketExtractor**: Extract from @websocket handlers
2. **ChannelsPluginExtractor**: Extract from ChannelsPlugin
3. **Operation direction inference**: send/receive detection

### Extraction Logic
```python
# WebSocket Handler → Channel
@websocket("/chat/{room}")
async def chat(socket: WebSocket, room: str) -> None:
    ...

# Extracts:
# - Channel: /chat/{room}
# - Parameter: room (string)
# - Operations: inferred from handler body
```

### Patterns to Follow
- Iterate over app.routes for WebSocketRoute instances
- Access ChannelsPlugin from app plugins
- Use handler signatures for type extraction

### Acceptance Criteria
- [ ] WebSocket handlers discovered automatically
- [ ] Path parameters extracted as channel parameters
- [ ] ChannelsPlugin channels extracted
- [ ] Operation direction inferred correctly
- [ ] Message types extracted from signatures
- [ ] 90% test coverage

### Dependencies
- PRD-001 (spec objects)
- PRD-002 (schema generation)

---

## PRD-004: Document Generation

### Description
Implement the main document generator that orchestrates all extractors and produces a complete AsyncAPI document.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-004-document-generation/`

### Files to Create
- `src/litestar_asyncapi/_asyncapi/generator.py`

### Files to Modify
- `src/litestar_asyncapi/config.py` (expand AsyncAPIConfig)
- `src/litestar_asyncapi/plugin.py` (add generation logic)

### Tests
- `src/tests/unit/test_generator.py`
- `src/tests/integration/test_full_generation.py`

### Key Components
1. **AsyncAPIGenerator**: Main orchestration class
2. **Reference resolution**: Convert inline to $ref
3. **Component deduplication**: Merge common schemas
4. **Validation**: Validate against AsyncAPI schema

### Generator Flow
```
AsyncAPIConfig
      │
      ▼
  Generator
      │
      ├── WebSocket Extractor
      │         │
      │         ▼
      │    Channels
      │         │
      ├── Channels Extractor
      │         │
      │         ▼
      │    More Channels
      │         │
      ├── Schema Generator
      │         │
      │         ▼
      │    Components
      │
      ▼
AsyncAPI Document
```

### Patterns to Follow
- Reference `litestar/_openapi/plugin.py`
- Lazy evaluation for performance
- Cache generated schema

### Acceptance Criteria
- [ ] Complete AsyncAPI document generated
- [ ] All handlers included
- [ ] All channels included
- [ ] Components populated with schemas
- [ ] References resolved correctly
- [ ] Document validates against AsyncAPI spec
- [ ] 90% test coverage

### Dependencies
- PRD-001 (spec objects)
- PRD-002 (schema generation)
- PRD-003 (handler discovery)

---

## PRD-005: Render Plugins

### Description
Implement render plugins for serving AsyncAPI documentation in JSON, YAML, and HTML formats.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/`

### Files to Create
- `src/litestar_asyncapi/plugins.py`

### Files to Modify
- `src/litestar_asyncapi/plugin.py` (route registration)
- `src/litestar_asyncapi/__init__.py` (exports)

### Tests
- `src/tests/unit/test_plugins.py`
- `src/tests/integration/test_routes.py`

### Render Plugins
1. **JsonRenderPlugin**: Serve asyncapi.json
2. **YamlRenderPlugin**: Serve asyncapi.yaml
3. **AsyncAPIStudioPlugin**: HTML UI viewer

### HTML Template (Studio)
```html
<!DOCTYPE html>
<html>
<head>
    <title>AsyncAPI Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/@asyncapi/react-component@latest/styles/default.min.css">
</head>
<body>
    <div id="asyncapi"></div>
    <script src="https://unpkg.com/@asyncapi/react-component@latest/browser/standalone/index.js"></script>
    <script>
        AsyncApiStandalone.render({
            schema: {{ schema | safe }},
            config: { show: { sidebar: true } }
        }, document.getElementById('asyncapi'));
    </script>
</body>
</html>
```

### Patterns to Follow
- Mirror `litestar/openapi/plugins.py` structure
- Abstract base class with render() method
- Route registration via on_app_init()

### Acceptance Criteria
- [ ] JSON endpoint serves valid JSON
- [ ] YAML endpoint serves valid YAML
- [ ] UI endpoint renders interactive documentation
- [ ] Routes registered at configured paths
- [ ] Content-Type headers correct
- [ ] 90% test coverage

### Dependencies
- PRD-004 (document generation)

---

## PRD-006: Advanced Features

### Description
Implement advanced AsyncAPI features including traits, custom decorators, and additional protocol bindings.

**Sub-PRD Workspace**: `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/`

### Files to Create
- `src/litestar_asyncapi/decorators.py`
- `src/litestar_asyncapi/spec/bindings/kafka.py` (optional)
- `src/litestar_asyncapi/spec/bindings/amqp.py` (optional)

### Tests
- `src/tests/unit/test_decorators.py`
- `src/tests/integration/test_advanced.py`

### Features
1. **Operation Traits**: Reusable operation properties
2. **Message Traits**: Reusable message properties
3. **Custom Decorators**: Explicit AsyncAPI metadata
4. **Additional Bindings**: Kafka, AMQP (if time permits)

### Decorator API
```python
from litestar_asyncapi import asyncapi_operation, asyncapi_message

@websocket("/events")
@asyncapi_operation(
    action="receive",
    title="Event Stream",
    description="Receive real-time events",
    tags=["events"],
)
async def events(socket: WebSocket) -> None:
    ...

@asyncapi_message(
    name="EventMessage",
    title="Event",
    content_type="application/json",
)
class Event:
    type: str
    data: dict[str, Any]
```

### Patterns to Follow
- Decorators store metadata in handler attributes
- Extractors check for decorator metadata first
- Fall back to automatic inference

### Acceptance Criteria
- [ ] Decorators allow explicit metadata
- [ ] Traits reused across operations/messages
- [ ] Decorator overrides automatic inference
- [ ] 90% test coverage

### Dependencies
- PRD-005 (render plugins)

---

## Summary Table

| PRD | Title | Files | Tests | Dependencies |
|-----|-------|-------|-------|--------------|
| 001 | Spec Foundation | ~20 | ~10 | None |
| 002 | Schema Generation | ~5 | ~5 | 001 |
| 003 | Handler Discovery | ~4 | ~3 | 001, 002 |
| 004 | Document Generation | ~2 | ~2 | 001, 002, 003 |
| 005 | Render Plugins | ~2 | ~2 | 004 |
| 006 | Advanced Features | ~3 | ~2 | 005 |

---

## Next Steps

1. Start with PRD-001 docs at `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md`
2. Use `tasks.md` within each sub-PRD directory as the checklist for that phase
3. Complete PRDs in order (001 → 006), updating each sub-PRD `tasks.md` and `recovery.md` as you go

---

## Quality Gates

Each PRD must pass before proceeding:
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] 90%+ coverage for modified modules
- [ ] No anti-patterns
- [ ] Pattern compliance verified
