# PRD-004: Document Generation (Orchestration)

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Dependencies**: PRD-001, PRD-002, PRD-003

---

## Intelligence Context

### Similar Implementations (Pattern References)

- `litestar/_openapi/plugin.py::OpenAPIPlugin`
  - lazy build/caching of spec + dict schema
  - router creation and handler registration
  - route collection/invalidation logic
- `litestar/openapi/config.py::OpenAPIConfig.to_openapi_schema()`
  - config-driven spec construction and defaults

### Patterns to Follow

- Separate *spec construction* (AsyncAPI root object) from *rendering* (bytes for JSON/YAML/UI).
- Cache at two levels:
  - spec object (`AsyncAPI`)
  - rendered dict (`dict[str, Any]`) for serialization
- Keep orchestration logic in one place (`AsyncAPIGenerator`) and keep extractors pure.

---

## 1. Problem Statement

After PRD-001/2/3, we can:
- represent AsyncAPI documents in code
- generate JSON Schemas for types
- discover websocket/channels structure

We still need a single orchestration layer to:
1. build a full AsyncAPI document from an application instance and config
2. assemble components and `$ref` maps
3. expose a stable “document dict” consumed by render plugins (PRD-005)

---

## 2. Goals / Non-Goals

### Goals

1. Implement the main generator that produces an AsyncAPI root document from:
   - `AsyncAPIConfig`
   - Litestar app instance (routes, plugins)
2. Build and attach:
   - `servers`
   - `channels`
   - `operations`
   - `components.schemas` (and other component sections as needed)
3. Provide caching and invalidation hooks for performance.

### Non-Goals

- No documentation endpoints or UI rendering (PRD-005).
- No advanced trait/decorator override mechanism (PRD-006).

---

## 3. Acceptance Criteria

1. **AC-401: End-to-end document build**
   - A Litestar app with websocket handlers yields a complete AsyncAPI document object.
2. **AC-402: Components population**
   - Schema registry output is placed into `components.schemas` deterministically.
3. **AC-402a: attrs component schemas**
   - attrs payload types used anywhere in discovered channels/messages appear under `components.schemas` and are
     referenced via `$ref`.
3. **AC-403: Caching**
   - Repeated requests do not rebuild the document unless invalidated.
4. **AC-404: Integration tests**
   - One integration test builds a full document and asserts key structural properties.

---

## 4. Technical Approach

### 4.1 Generator class

Add an internal generator object:

```
src/litestar_asyncapi/_asyncapi/generator.py
  class AsyncAPIGenerator:
    def __init__(self, *, config: AsyncAPIConfig, app: Litestar): ...
    def build_asyncapi(self) -> AsyncAPI: ...
    def build_schema(self) -> dict[str, Any]: ...
```

Responsibilities:
- call extractors (PRD-003) to get discovered channels/operations
- call schema generation (PRD-002) to build schemas and register components
- construct spec objects (PRD-001) and connect references

### 4.2 Config-driven root fields

The AsyncAPI root should be primarily config-driven:
- `info` from config
- `servers` from config (with sensible defaults)
- `defaultContentType` from config, defaulting to `application/json`

Extraction-driven:
- `channels`, `operations`
- `components.schemas` and related sections

### 4.3 Cache and invalidation strategy

Mirror OpenAPI plugin behavior:
- cache the built AsyncAPI object and schema dict
- invalidate when:
  - a new route is registered (if we implement `ReceiveRoutePlugin`)
  - explicitly requested via config / method (fallback)

Initial implementation can start with “cache on first request” with manual invalidation; add receive-route invalidation
later if complexity is high.

---

## 5. Testing Strategy

### Unit tests

- generator builds a document for a simple app:
  - one websocket listener route
  - one websocket stream route
- registry output appears in components
- stable output with repeated calls (caching)

### Integration tests

- build full document schema and assert:
  - `asyncapi` version string present
  - `info.title` is correct
  - at least one channel exists
  - operations have correct `action`

---

## 6. Deliverables

- `src/litestar_asyncapi/_asyncapi/generator.py`
- extensions to `AsyncAPIConfig` and `AsyncAPIPlugin` to call generator
- tests validating end-to-end document construction
