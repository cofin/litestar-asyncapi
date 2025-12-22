# Pattern Analysis: AsyncAPI Plugin

**Created**: 2025-12-17
**Scope**: Parent workspace `specs/active/asyncapi-plugin/`

This document captures the most important implementation patterns to mirror from Litestar's OpenAPI system and
the constraints we should carry into `litestar-asyncapi`.

## Similar Implementations (Primary References)

These are the high-signal sources to mirror for structure and behavior:

1. `litestar/openapi/config.py`
   - Config dataclass pattern, normalization, default plugins, and schema creation entrypoint.
2. `litestar/_openapi/plugin.py`
   - Init plugin lifecycle, route collection, schema caching, and router creation for docs endpoints.
3. `litestar/openapi/plugins.py`
   - Render plugin base class and concrete JSON/YAML/UI renderers.
4. `litestar/openapi/spec/base.py`
   - Spec object serialization pattern (`BaseSchemaObject.to_schema()`).
5. `litestar/_openapi/datastructures.py`
   - `SchemaRegistry` key normalization, deduplication, and `$ref` path assignment.
6. `litestar/_openapi/schema_generation/schema.py`
   - Type → schema mapping, constrained fields, plugin-based schema generation, and examples.

## Key Patterns to Mirror

### 1) Config as the “root of truth”

Pattern:
- A dataclass-based config object owns user-facing settings (title/version/description/etc.).
- It normalizes inputs in `__post_init__` (paths, defaults, plugin selection).
- It provides a single entrypoint to build a root spec object (e.g. `to_openapi_schema()`).

AsyncAPI adaptation:
- `AsyncAPIConfig` should expose `to_asyncapi_schema()` (or equivalent) returning the AsyncAPI root object.
- Normalize configured base path and per-render-plugin paths early.

### 2) Plugin owns caching + route registration

Pattern:
- The plugin stores config + built spec object + rendered schema dict, all cached lazily.
- The plugin creates a dedicated router for schema routes and UI routes.
- The plugin can rebuild when routes change (OpenAPI plugin uses `ReceiveRoutePlugin` to track routes).

AsyncAPI adaptation:
- If we can observe route registration, we should reset caches when new websocket/channel routes are registered.
- If not, build lazily on first request and allow explicit invalidation (config flag or method).

### 3) Render plugins are composable and self-contained

Pattern:
- A base render plugin defines `paths` and `render()`.
- JSON/YAML plugins primarily format bytes and set the correct media type.
- UI plugins render HTML and often reference CDNs.

AsyncAPI adaptation:
- Provide JSON and YAML endpoints first.
- Provide a React-component based UI via CDN (as described in the parent PRD), with template overrides possible.

### 4) Spec objects are dataclasses with consistent serialization

Pattern:
- A `BaseSchemaObject` uses dataclass reflection to serialize.
- It normalizes field names to camelCase and handles special keys (`$ref`, etc.).
- It skips `None` fields and supports nested spec objects.

AsyncAPI adaptation:
- AsyncAPI spec objects should follow the same approach: dataclasses + `to_schema()` on a shared base.
- Use consistent aliasing and normalization rules so objects are deterministic and diff-friendly.

### 5) Schema registry drives $ref deduplication

Pattern:
- A schema registry creates stable keys per Python type.
- It manages a “components/schemas” map and rewrites `$ref` paths to be short but unique.
- It can error when a key collides across incompatible types.

AsyncAPI adaptation:
- AsyncAPI’s reusable components should include schemas/messages/parameters/etc.
- Start with schema components for payloads and expand to messages later.
- Ensure schema generation supports Litestar-supported model libraries (including attrs).

## AsyncAPI-Specific Notes (Where We Diverge)

1. **Channels vs Paths**: AsyncAPI channels are not HTTP path items; extraction must map websocket routes and channel
   definitions into AsyncAPI channel + operation objects.
2. **Operations are first-class**: AsyncAPI operations include an `action` (`send`/`receive`) and may not live
   “inside” channels the same way OpenAPI operations live inside paths.
3. **Bindings**: AsyncAPI bindings are extensible per protocol (websocket first); keep them in a dedicated
   `spec/bindings/` namespace and isolate binding serialization.

## Open Questions to Validate Early

1. How best to infer operation direction for websocket handlers in Litestar (body inspection vs explicit metadata)?
2. How to represent message payload types from handler annotations (socket receive vs send patterns)?
3. How to expose configuration hooks for ChannelsPlugin integration without tight coupling?
