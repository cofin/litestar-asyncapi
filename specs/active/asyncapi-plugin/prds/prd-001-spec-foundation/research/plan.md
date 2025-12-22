# Research Notes: PRD-001 AsyncAPI Spec Foundation

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17
**Purpose**: Capture PRD-001 specific decisions and implementation references

---

## 1. What we need from the AsyncAPI 3.0.0 specification (for Phase 1)

Phase 1 is focused on the object model and serialization rules, not on extraction or generation. That means the critical
inputs are:

1. The list of objects we must model to build a minimally useful AsyncAPI document.
2. The required/optional fields for those objects.
3. The serialization rules (especially naming and extension fields).

For our use, the spec “shape” needs to support:
- a root document with `asyncapi`, `info`, and `channels`
- message payload schemas (`Schema` objects) and `$ref` reuse through `components`
- protocol bindings for WebSocket

---

## 2. Serialization strategy (mirroring Litestar OpenAPI)

Litestar’s OpenAPI spec object model uses:
- `@dataclass` for each spec type
- a shared `BaseSchemaObject.to_schema()` that:
  - skips `None` values
  - normalizes keys (`snake_case` → `camelCase`, `$ref`, reserved words)
  - recursively serializes nested spec objects, dicts, lists, and Enums

This pattern is high-value because it yields:
- deterministic outputs (stable key naming and omission rules)
- minimal hand-written dict-building logic across the spec surface
- easy testing (instantiate dataclasses, assert dict output)

AsyncAPI should copy this approach, but with a key decision: **use `@dataclass(slots=True)`** to align with this
repository’s “slots required” rule.

---

## 3. Required object set for early milestones

Even though AsyncAPI is large, PRD-004 (document generation) only needs a subset to ship a useful first version:

### Root + metadata
- AsyncAPI root document (version string, id, info, defaultContentType)
- Info (title, version, description)
- Contact / License (optional but common)

### Topology
- Servers (even a default server) to anchor protocol + host details
- Channels with an address and optional parameters/bindings
- Operations (send/receive) tied to channels
- Messages referenced by operations, with payload schema

### Reuse and references
- Components: at least `schemas` and `messages` (other sections optional initially)
- `$ref` representation

### Schema model
We need a schema model compatible with how we plan to generate schemas:
- types (string, number, object, array, boolean, null)
- constraints (min/max, pattern, enum, oneOf/anyOf/allOf, properties, required)
- `$ref` support

### Bindings (WebSocket)
AsyncAPI 3.0 uses protocol bindings which are namespaced. For WebSockets, we will model binding objects in:
`spec/bindings/websocket.py` and keep them isolated from core objects.

---

## 4. Testing approach for Phase 1

Testing should validate behavior rather than spec completeness:

1. **Serializer unit tests**:
   - key normalization
   - alias metadata
   - enum serialization
   - recursive object graphs
2. **Representative “mini document” tests**:
   - build a small AsyncAPI document with:
     - 1 server
     - 1 channel with a parameter
     - 2 operations (send/receive) each referencing a message
     - message payload schema(s)
   - assert `to_schema()` yields a dict matching expected structure

This gives confidence for PRD-004 without requiring full AsyncAPI schema validation yet.

---

## 5. Implementation decisions (Phase 1)

### Decision: Key normalization rules

Adopt Litestar’s rules for:
- `ref` → `$ref`
- snake_case → camelCase
- underscore handling in keys

This keeps output consistent with existing Litestar spec serialization and reduces surprises for users familiar with
Litestar’s OpenAPI.

### Decision: Field aliasing

Support field metadata aliasing so that `x-` extensions (and other custom keys) can be represented without contorting
Python identifiers.

### Decision: Scope boundaries

Do not embed document assembly logic into spec objects. Spec objects should be “dumb” containers + serializer. Assembly
and discovery belong in PRD-004 / PRD-003.
