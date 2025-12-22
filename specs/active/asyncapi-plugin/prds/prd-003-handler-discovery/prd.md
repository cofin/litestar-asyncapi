# PRD-003: Handler Discovery (WebSocket + ChannelsPlugin)

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Dependencies**: PRD-001 (spec foundation), PRD-002 (schema generation)

---

## Intelligence Context

### Similar Implementations (Pattern References)

- `litestar/routes/websocket.py::WebSocketRoute` - canonical websocket route type
- `litestar/routes/base.py::BaseRoute` - `path_format` and `path_parameters` parsing
- `litestar/handlers/websocket_handlers/*` - websocket handler variants with typed payload hooks:
  - `WebsocketRouteHandler` (basic)
  - `WebsocketListenerRouteHandler` (typed `data` + typed return)
  - `WebSocketStreamHandler` (typed stream item return)
- `litestar/channels/plugin.py::ChannelsPlugin` - channels configuration and websocket handler generation

### Patterns to Follow

- Prefer extracting from stable public route structures (`BaseRoute.path_format`, `path_parameters`).
- Infer message schemas from the most explicit source available:
  1) typed websocket listener/stream handlers
  2) explicit metadata (PRD-006 decorators)
  3) safe fallback schemas when unknown

---

## 1. Problem Statement

The AsyncAPI document generator needs a list of channels, operations, and message types. Litestar applications express
async APIs through:

- websocket routes (plain websocket handlers, listener handlers, stream handlers)
- ChannelsPlugin channel names and broadcast payloads

This phase implements the extraction layer that converts Litestar routes and channel definitions into AsyncAPI spec
objects (channels + operations + message references), ready for PRD-004 orchestration.

---

## 2. Goals / Non-Goals

### Goals

1. Discover websocket routes and translate them into AsyncAPI channels.
2. Extract channel parameters from Litestar path parameters.
3. Infer send/receive operations and message payload schemas when possible.
4. Optionally integrate ChannelsPlugin-defined channels into AsyncAPI channels.
5. Provide a stable internal “extraction result” representation consumed by PRD-004.

### Non-Goals

- No schema rendering endpoints (PRD-005).
- No advanced decorators/traits override mechanism (PRD-006), except for leaving an extension point.
- No full AsyncAPI schema validation (PRD-004).

---

## 3. Acceptance Criteria

1. **AC-301: WebSocket route discovery**
   - Finds all `WebSocketRoute` instances and extracts `path_format`.
2. **AC-302: Parameter extraction**
   - Converts `BaseRoute.path_parameters` into AsyncAPI channel parameters with schemas derived from parameter types.
3. **AC-303: Typed handler inference**
   - For `WebsocketListenerRouteHandler`, infer:
     - receive message schema from the `data` parameter annotation
     - send message schema from the handler return annotation (if not `None`)
   - For `WebSocketStreamHandler`, infer:
     - send message schema from the stream item type
4. **AC-304: Safe fallback**
   - For untyped websocket handlers, extraction still yields a valid channel definition without crashing.
5. **AC-305a: attrs payload support**
   - If a typed handler uses an attrs class as a payload type, schema generation produces a `$ref` schema component and
     extraction references it (no special-case logic in extractors beyond using the schema generator).
5. **AC-305: ChannelsPlugin extraction**
   - When a ChannelsPlugin is present, extract known channel names (when available) and represent them as AsyncAPI
     channels with at least a placeholder message schema.
6. **AC-306: Test coverage**
   - 90%+ coverage across extractor modules with unit tests and at least one integration test.

---

## 4. Technical Approach

### 4.1 Extractor API (proposed)

Define internal extractor classes that return spec objects or intermediate structures:

- `WebSocketExtractor.extract(app) -> list[DiscoveredChannel]`
- `ChannelsPluginExtractor.extract(app) -> list[DiscoveredChannel]`

Where `DiscoveredChannel` contains:
- `address` / `path_format`
- `parameters`
- `operations` (send/receive)
- message type fields or already-generated message schema references

PRD-004 will merge these into a final AsyncAPI root document.

### 4.2 WebSocket handler type inference

Litestar provides several websocket handler “shapes”:

1) **Plain websocket handler** (`@websocket`)
   - No supported `data` parameter; cannot infer payload type from signature alone.
   - Strategy:
     - create channel with parameters
     - omit operations/messages unless explicit metadata is provided (PRD-006), or
     - optionally include a permissive message schema (`payload: {}`) when configured.

2) **Websocket listener** (`@websocket_listener`)
   - Requires a `data` parameter; route handler stores parsed field definitions.
   - Strategy:
     - receive operation: message payload derived from `data` annotation
     - if return type is not `None`, add send operation with that payload schema

3) **Websocket stream** (`@websocket_stream`)
   - Return type is `AsyncGenerator[T, ...]` and route handler stores stream item type.
   - Strategy:
     - send operation: message payload derived from stream item type

### 4.3 Operation direction semantics

AsyncAPI operations are first-class objects with `action: send|receive`.

Mapping rules:
- “Receive” operation corresponds to *messages the application receives from clients*.
- “Send” operation corresponds to *messages the application sends to clients*.

This aligns with the Litestar handler perspective:
- listener `data` is received from client → `receive`
- stream item is sent to client → `send`

### 4.4 ChannelsPlugin extraction strategy

ChannelsPlugin can expose channels in two ways:

1. If `create_ws_route_handlers=True`, websocket handlers are generated for channels. In that case, websocket discovery
   already finds them and we can treat them as websocket channels.
2. Otherwise, we still want to document the channel namespace:
   - “Known channels” can be extracted from the plugin’s internal channel mapping (implementation detail).
   - If only `arbitrary_channels_allowed=True`, represent a wildcard channel pattern only when enabled via config.

Because ChannelsPlugin does not currently expose a public `channels` attribute, initial extraction may rely on its
internal `_channels` mapping. This should be treated as best-effort and guarded with feature flags to avoid breaking
changes.

---

## 5. Testing Strategy

### Unit tests

- WebSocket route discovery:
  - build a minimal Litestar app with websocket routes
  - assert channel addresses match `path_format`
- Parameter extraction:
  - websocket route with typed path params (`{room:int}`) yields AsyncAPI channel parameters with correct schema types
- Listener inference:
  - a `@websocket_listener` handler with `data: MyModel` yields a receive message schema referencing `MyModel`
- Stream inference:
  - a `@websocket_stream` handler returning `AsyncGenerator[MyModel, None]` yields send message schema

### Integration test

Create an app with:
- one plain websocket handler
- one listener
- one stream
and assert extraction yields three channels and the correct operation directions for the typed handlers.

---

## 6. Deliverables

- Extractors under `src/litestar_asyncapi/_asyncapi/extractors/`
- Integration points to call schema generation (PRD-002) for payload types
- Test suite for discovery and inference
