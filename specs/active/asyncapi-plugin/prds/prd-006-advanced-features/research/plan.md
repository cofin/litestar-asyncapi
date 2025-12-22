# Research Notes: PRD-006 Advanced Features

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17

---

## 1. Why explicit metadata is necessary

Litestar’s plain websocket handler API is deliberately low-level:
- inbound payload types are not expressed in the handler signature
- receiving is performed by calling `socket.receive_*()` methods that return untyped values (`Any`)

As a result, “automatic inference” cannot reliably determine:
- inbound message payload types
- outbound message payload types
- correlation IDs, headers, tags, security, etc.

AsyncAPI is fundamentally about message contracts. Without explicit metadata, the plugin would either:
- produce incomplete specs (channels without messages), or
- guess incorrectly (worse than incomplete)

Therefore, the plugin must offer an override mechanism.

---

## 2. Metadata attachment options

### Option A: Attach to the user function (attributes)

Pros:
- easy to implement

Cons:
- can break when handlers are wrapped by route handler classes or decorators
- controller binding can change the callable identity

### Option B: Store on route handler `opt` (recommended)

Pros:
- designed for arbitrary metadata
- accessible during route discovery/extraction
- composes better with Litestar ownership layers and controllers

Cons:
- requires careful handling to ensure metadata is merged if multiple decorators are applied

Recommendation:
- Use `opt["asyncapi"]` as the canonical storage location.

---

## 3. Precedence and merging rules

Key design requirement: metadata should be able to override inference without surprising users.

Proposed precedence:
1. Decorator metadata wins for any explicitly specified field.
2. Inferred values fill in missing fields.
3. Fallback schema or omission applies only when both are absent.

Merging should be “field-by-field”, not all-or-nothing, to keep decorators ergonomic (users shouldn’t need to specify
every field just to set a title).

---

## 4. Trait support rationale

AsyncAPI traits allow repeated properties (tags, bindings, security, etc.) to be defined once and reused.

This is valuable for large systems where many channels share common:
- security requirements
- tags and external docs
- bindings configuration

We should add trait support once the basic document generation works to avoid over-complicating earlier phases.
