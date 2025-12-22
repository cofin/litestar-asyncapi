# PRD-005: Render Plugins (JSON/YAML/UI)

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Dependencies**: PRD-004 (document generation)

---

## Intelligence Context

### Similar Implementations (Pattern References)

- `litestar/openapi/plugins.py`
  - base render plugin interface
  - JSON/YAML renderers
  - HTML UI renderers (Rapidoc/Redoc/Swagger/etc.)
- `litestar/_openapi/plugin.py::create_openapi_router()`
  - router creation and handler registration per render plugin

### Patterns to Follow

- Render plugins are small and composable.
- The plugin registers a router and for each configured render plugin creates a handler at its configured paths.
- JSON rendering uses Litestar serializer hooks (type encoders).
- YAML rendering converts to builtins first to strip sentinel values if needed.

---

## 1. Problem Statement

To be useful, the AsyncAPI document must be served in standard formats:

- `asyncapi.json` for tools and codegen
- `asyncapi.yaml` for readability and compatibility
- an interactive UI (AsyncAPI React component / studio)

This phase adds render plugins and route registration, mirroring Litestar OpenAPI’s UX and extension model.

Implementation note: the generated schema must reflect Litestar-supported model libraries used in message payload types
(including attrs), but render plugins remain agnostic to the underlying Python model types.

---

## 2. Goals / Non-Goals

### Goals

1. Provide render plugins for JSON and YAML output.
2. Provide an HTML UI endpoint using a CDN-delivered AsyncAPI React component.
3. Register docs endpoints in Litestar app lifecycle with configurable base path.
4. Make render plugins extensible so users can provide custom UIs.

### Non-Goals

- No advanced decorators/traits (PRD-006).
- No bundling of UI assets locally (defer; CDN first).

---

## 3. Acceptance Criteria

1. **AC-501: JSON endpoint**
   - Serves a valid AsyncAPI JSON document at a configurable path.
2. **AC-502: YAML endpoint**
   - Serves a valid AsyncAPI YAML document at a configurable path.
3. **AC-503: UI endpoint**
   - Serves an HTML page rendering the AsyncAPI schema via the AsyncAPI React component.
4. **AC-504: Router structure**
   - Docs routes are grouped under a dedicated router and excluded from the app schema.
5. **AC-505: Tests**
   - Integration tests confirm routes exist and return expected media types.

---

## 4. Technical Approach

### 4.1 Render plugin interface

Create an abstract base class similar to `OpenAPIRenderPlugin`:

- constructor accepts `path` (string or list), `media_type`, and optional HTML parameters (favicon/style)
- defines:
  - `render(request, asyncapi_schema_dict) -> bytes`
  - `render_json(request, asyncapi_schema_dict) -> bytes` helper
  - `has_path(path) -> bool`
  - `receive_router(router)` hook for plugins that need extra routes

### 4.2 Concrete plugins

1. **JsonRenderPlugin**
   - defaults: `/asyncapi.json`
   - media type: `application/vnd.asyncapi+json` (or `application/json` if Litestar lacks enum)
2. **YamlRenderPlugin**
   - defaults: `/asyncapi.yaml` and `/asyncapi.yml`
   - media type: `application/vnd.asyncapi+yaml` (or `application/yaml`)
3. **AsyncAPIStudioRenderPlugin** (name TBD)
   - default: `/asyncapi`
   - renders HTML embedding the AsyncAPI React component and passing the schema via inline JSON

### 4.3 Router creation

Mirror OpenAPI plugin:
- create a router rooted at config `path` (default e.g. `/asyncapi`)
- for each plugin:
  - register a `@get` handler at plugin paths
  - handler calls `plugin.render(request, asyncapi_schema_dict)`
- add a fallback 404 handler for unknown docs paths (optional)
- allow plugin to receive router instance for extra setup

### 4.4 Serialization + caching integration

Routes should call the cached schema dict from PRD-004:
- `AsyncAPIPlugin.provide_asyncapi_schema()` (name TBD)

Render plugins should not rebuild the schema.

---

## 5. Testing Strategy

### Integration tests

- Create Litestar app with AsyncAPIPlugin enabled.
- Assert:
  - GET `/asyncapi/asyncapi.json` returns 200 and JSON media type
  - GET `/asyncapi/asyncapi.yaml` returns 200 and YAML media type
  - GET `/asyncapi/` returns 200 and HTML content type

### Unit tests

- Json plugin returns bytes and uses Litestar serializer hooks.
- YAML plugin emits YAML bytes and includes expected top-level keys.

---

## 6. Deliverables

- `src/litestar_asyncapi/plugins.py` render plugin implementations
- plugin route registration in `src/litestar_asyncapi/plugin.py`
- tests covering routes + content types
