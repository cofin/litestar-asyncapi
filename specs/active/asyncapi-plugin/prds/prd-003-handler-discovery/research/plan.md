# Research Notes: PRD-003 Handler Discovery

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17

---

## 1. Litestar websocket route model

Litestar represents websocket endpoints as `WebSocketRoute` objects. Each route:

- inherits `BaseRoute`
- exposes `path_format` which removes path parameter type suffixes (e.g. `/chat/{room:int}` → `/chat/{room}`)
- exposes `path_parameters` as a mapping of parameter name to a `PathParameterDefinition` containing:
  - the parameter name
  - the resolved Python type (e.g. `int`)
  - (optionally) a parser

This is ideal for AsyncAPI channel extraction:
- channel `address` can use `path_format`
- channel `parameters` can be generated directly from `path_parameters`

---

## 2. Websocket handler varieties and what they imply for AsyncAPI

### 2.1 Plain websocket handlers (`@websocket`)

Plain websocket handlers do not accept a `data` argument and therefore do not expose a typed inbound payload shape via
signature. Any message contract is encoded in application logic (calls to `socket.receive_json()` etc.).

Implication:
- We can always document the channel address and parameters.
- We cannot reliably infer message schemas without additional metadata.
- The plugin must support a “safe fallback” mode and allow explicit overrides in PRD-006.

### 2.2 Listener handlers (`@websocket_listener`)

Listeners are more structured:
- they require a `data` parameter
- Litestar stores the parsed “data field” and “return field” in the route handler instance

This is our best source for automatic inference:
- `data` type → AsyncAPI `receive` operation message payload schema
- return type (if not `None`) → AsyncAPI `send` operation message payload schema

Schema generation must support Litestar-supported model libraries used in these annotations (including attrs), so the
extractor can treat all payload types uniformly.

### 2.3 Stream handlers (`@websocket_stream`)

Stream handlers return `AsyncGenerator[T, ...]` and Litestar stores the stream item type in the route handler.

Implication:
- `T` → AsyncAPI `send` operation message payload schema
- There may be no inbound message shape to infer; treat as “send-only” by default

---

## 3. Mapping Litestar semantics to AsyncAPI operations

AsyncAPI defines operations with an `action`:
- `receive`: app receives messages from clients
- `send`: app sends messages to clients

We should always map “direction” from the app’s perspective (consistent across websocket and channels).

---

## 4. ChannelsPlugin considerations

ChannelsPlugin can be used as a pub/sub abstraction independent of websocket routes. It can optionally generate websocket
handlers (`create_ws_route_handlers=True`), but it can also operate without them.

To document ChannelsPlugin channels:
- Prefer documenting the same websocket routes if the plugin generates them.
- Otherwise, extract channel names from the plugin’s internal mapping.

Because ChannelsPlugin does not expose a stable public attribute for “declared channels”, early versions may rely on
`_channels` internal state. This should be:
- guarded behind feature flags in `AsyncAPIConfig`
- best-effort and tolerant of changes

Future improvements:
- contribute a public `channels` property upstream (if acceptable) to make extraction stable.
