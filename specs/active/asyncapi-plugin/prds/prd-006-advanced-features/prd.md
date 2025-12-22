# PRD-006: Advanced Features (Decorators, Traits, Additional Bindings)

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Dependencies**: PRD-005 (render plugins), PRD-003 (discovery)

---

## Intelligence Context

### Similar Implementations (Pattern References)

- Litestar route handler metadata patterns:
  - `RouteHandler.opt` (arbitrary metadata stored on handlers)
  - handler decorators that enrich route handlers at registration time
- The OpenAPI ecosystem pattern:
  - provide automatic inference first
  - allow explicit overrides via decorator metadata for hard-to-infer behavior

### Why this phase exists

Automatic discovery will never fully infer async message contracts for plain websocket handlers because Litestar’s plain
websocket API is intentionally flexible (`receive_json()` returns `Any` and handler signatures do not include payload
types). This phase provides a first-class, ergonomic override mechanism.

---

## 1. Problem Statement

For many real-world websocket handlers, we cannot infer:
- inbound message payload type(s)
- outbound message payload type(s)
- operation summaries/descriptions/tags
- message headers/contentType
- correlation IDs and traits

To achieve high-quality AsyncAPI docs, users need an explicit way to provide this metadata without abandoning automatic
discovery.

---

## 2. Goals / Non-Goals

### Goals

1. Provide decorators for:
   - operation metadata (action, title/summary/description, tags, security)
   - message metadata (name/title/contentType, headers schema, correlation ID)
2. Allow metadata to:
   - override automatic inference
   - augment automatically inferred structures (e.g., add tags)
3. Add support for operation and message traits as reusable components.
4. Optionally add additional bindings (Kafka, AMQP) behind feature flags.

Model support note:
- Decorator-specified payload/message types may be attrs classes; schema generation and `$ref` reuse must work uniformly
  across attrs, dataclasses, msgspec, TypedDict, and Pydantic.

### Non-Goals

- No attempt to fully infer plain websocket message types without metadata.
- No breaking changes to earlier phases; decorators should be additive.

---

## 3. Acceptance Criteria

1. **AC-601: Decorator metadata**
   - Decorators can attach metadata to websocket handlers without affecting runtime behavior.
2. **AC-602: Override precedence**
   - Extractors apply decorator metadata first; fall back to inference second; fallback schema last.
3. **AC-603: Traits support**
   - Operation and message traits can be defined once and reused across operations/messages.
4. **AC-604: Tests**
   - Unit tests verify decorator attachment and extractor override behavior.

---

## 4. Technical Approach

### 4.1 Metadata storage strategy

Preferred approach:
- Store AsyncAPI metadata on the **route handler** via `route_handler.opt` with a reserved key, e.g. `opt["asyncapi"]`.

Rationale:
- `opt` is designed for arbitrary handler metadata.
- It avoids direct attribute injection onto user callables.
- It composes well with controllers and ownership layers.

Decorator signature examples:

```python
@asyncapi_operation(action="receive", title="Chat inbound", tags=["chat"])
@websocket_listener("/chat/{room:str}")
async def chat(socket: WebSocket, data: ChatMessage, room: str) -> None:
    ...
```

### 4.2 Override policy

Extractor precedence:
1. If decorator provides explicit message schema/type, use it.
2. Else if handler type supports inference (listener/stream), infer from stored field definitions.
3. Else use fallback schema or omit messages based on config.

### 4.3 Traits

Implement traits as spec-level reusable objects:
- define `OperationTrait` and `MessageTrait` in spec model (PRD-001 may already include placeholders)
- allow config to register shared traits, or infer traits from repeated decorator patterns

### 4.4 Additional protocol bindings (optional)

Add Kafka/AMQP binding object models behind feature flags:
- spec/bindings/kafka.py
- spec/bindings/amqp.py

These should not be required for the base plugin and can ship later.

---

## 5. Testing Strategy

### Unit tests

- decorators attach metadata to route handler `opt`
- extractor reads metadata and overrides inferred message schemas
- traits reused correctly when referenced

### Integration test

- app with a plain websocket handler annotated via decorators yields a channel with send/receive operations and message
  schemas, without relying on inference.

---

## 6. Deliverables

- `src/litestar_asyncapi/decorators.py` decorator API
- extractor changes to apply override policy
- trait support in spec model and generator
- tests covering overrides and trait reuse
