# PRD-001: AsyncAPI Spec Foundation

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Scope**: Spec object model + serialization (no generation/extraction/routes)

---

## Intelligence Context

### Similar Implementations (Pattern References)

- `litestar/openapi/spec/base.py` - dataclass-driven spec serialization (`BaseSchemaObject.to_schema()`)
- `litestar/openapi/spec/*` - organization of spec objects per domain concept
- `litestar/openapi/spec/enums.py` - spec-level enums

### Patterns to Follow

- Dataclass spec objects with a shared base serializer (`to_schema()`).
- Field name normalization:
  - snake_case → camelCase
  - `ref` → `$ref`
  - special-cases such as `*_in` → `in`
- `None` values omitted from serialized output.
- Nested spec objects serialize recursively.
- Prefer `slots=True` dataclasses to match project slot requirements.

---

## 1. Problem Statement

The AsyncAPI plugin requires an internal representation of AsyncAPI 3.0 documents to generate stable JSON/YAML output.
Without a first-class spec object model, later phases (schema generation, handler extraction, document assembly, render
plugins) either become tightly coupled to raw dictionaries or must reinvent serialization and key normalization rules.

This phase establishes the canonical AsyncAPI 3.0 object model and serialization behavior that subsequent phases build
on.

---

## 2. Goals / Non-Goals

### Goals

1. Provide a complete (or near-complete) AsyncAPI 3.0.0 spec object model needed by the plugin’s generation pipeline.
2. Provide deterministic serialization to Python primitives for JSON/YAML rendering.
3. Establish a consistent module layout mirroring Litestar OpenAPI for familiarity and maintainability.
4. Include protocol binding models needed for the first supported protocol: WebSocket.

### Non-Goals

- No schema generation from Python types (PRD-002).
- No route/channel discovery or inference (PRD-003).
- No AsyncAPI document assembly orchestration (PRD-004).
- No docs endpoints or UI rendering (PRD-005).
- No advanced traits/decorators or extra protocol bindings (PRD-006).

---

## 3. Acceptance Criteria

1. **AC-001: Serialization correctness**
   - All implemented spec objects serialize to `dict[str, Any]` via `to_schema()`.
   - Serialization omits `None` values and recursively serializes nested objects.
   - Field names normalize predictably (camelCase; `$ref`; reserved words).
2. **AC-002: Deterministic output**
   - Serialization output is stable across runs given identical inputs (no reliance on unordered iteration).
3. **AC-003: WebSocket bindings**
   - WebSocket binding objects exist under `spec/bindings/websocket.py` and serialize correctly.
4. **AC-004: Test coverage**
   - Unit tests cover the base serializer and representative nested object graphs.
   - Coverage target: 95%+ for `src/litestar_asyncapi/spec/`.

---

## 4. Technical Approach

### 4.1 Package Layout

Mirror Litestar’s OpenAPI layout to reduce cognitive load:

```
src/litestar_asyncapi/spec/
  __init__.py
  base.py
  asyncapi.py
  info.py
  server.py
  channel.py
  operation.py
  message.py
  schema.py
  components.py
  reference.py
  security_scheme.py
  tag.py
  external_docs.py
  correlation_id.py
  reply.py
  enums.py
  bindings/
    __init__.py
    base.py
    websocket.py
```

### 4.2 Base Serialization (`BaseSchemaObject`)

Base behavior should:

- Iterate dataclass fields (optionally allowing override for custom ordering).
- Convert field names to the spec key:
  - `snake_case` → `camelCase`
  - `ref` → `$ref`
  - `schema_*` → the AsyncAPI field name when a prefix is reserved
  - Any additional reserved keywords mirrored from Litestar OpenAPI (`*_in` → `in`) where applicable.
- Support field metadata aliasing (e.g. `field(metadata={"alias": "x-custom"})`) for extension fields.
- Normalize values:
  - spec objects → `to_schema()`
  - dataclasses → dict (excluding `None`)
  - dicts → normalized recursively (excluding `None`)
  - lists → normalized recursively
  - Enums → `.value`

Implementation note:
- Prefer `@dataclass(slots=True)` for all spec objects.

### 4.3 Spec Object Coverage Strategy

The parent PRD targets broad AsyncAPI coverage. For this phase, prioritize:

1. Root document object and supporting metadata (`AsyncAPI`, `Info`, `Contact`, `License`).
2. Core topology objects (`Server`, `Channel`, `Operation`, `Message`).
3. Reusability constructs (`Components`, `Reference`).
4. Schema representation (`Schema`), focusing on what later schema generation needs (draft-07 aligned fields).
5. Binding scaffolding (`bindings/base.py`, `bindings/websocket.py`).

Objects that are not required for early plugin operation can be added later (still within PRD-001) but should not block
downstream phases if they are isolated and optional.

---

## 5. Testing Strategy

### Unit Tests

Create a dedicated unit test suite focused on serialization and normalization:

- `BaseSchemaObject.to_schema()`:
  - camelCase conversion
  - `$ref` mapping
  - alias metadata handling
  - recursive nesting
  - list/dict normalization
  - Enum serialization
- Representative object graphs:
  - `AsyncAPI(info=Info(...), channels={...}, components=Components(...))`
  - Channel with parameters, operation references, message payload schemas, and bindings

### Golden-File Testing (Optional)

If appropriate, add “golden” expected dict structures for a small document to catch regressions in key normalization.

---

## 6. File Changes

### Files to Create

See `specs/active/asyncapi-plugin/tasks.md` PRD-001 section for the full file list.

### Files to Modify

None required for this phase, except potentially exporting spec objects in the package `__init__` if needed for
downstream phases.

---

## 7. Risks & Mitigations

- **Risk**: AsyncAPI 3.0 model surface is large; we overbuild before proving generation.
  - **Mitigation**: Prioritize objects required for PRD-004, add the rest iteratively with tests.
- **Risk**: Serialization rules mismatch AsyncAPI expectations.
  - **Mitigation**: Keep normalization rules explicit, add tests for edge names, and validate sample output in PRD-004.

---

## 8. Deliverables

- `src/litestar_asyncapi/spec/` module tree with dataclass spec objects
- Deterministic `to_schema()` serialization from any root AsyncAPI document
- Unit tests covering serializer + representative objects
