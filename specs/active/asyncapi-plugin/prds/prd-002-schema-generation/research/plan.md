# Research Notes: PRD-002 AsyncAPI Schema Generation

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17

---

## 1. Why schema generation is a separate phase

AsyncAPI generation depends on accurate JSON Schema payloads. For Litestar OpenAPI, schema generation is the most
complex and most reused subsystem because:

- It must interpret Python’s typing system (generics, unions, literals, custom types).
- It must interoperate with multiple modeling libraries (Pydantic, attrs, dataclasses, msgspec, TypedDict).
- It must produce stable `$ref` keys so the spec is consistent across runs and merges.

Keeping this phase isolated allows us to:

- validate schema generation correctness independently of route extraction logic
- build a reusable internal API consumed by both websocket extraction and ChannelsPlugin extraction

---

## 2. Mapping to AsyncAPI needs

AsyncAPI 3.0 uses JSON Schema for message payloads and (optionally) headers. For our plugin, schema generation must
support at minimum:

- object schemas with properties and required fields
- nested object graphs
- arrays and maps/dicts
- union/optional semantics
- enums, literals, and constrained primitives
- reuse via `$ref` and collection into components

Unlike OpenAPI, the schema objects are not embedded in request/response bodies. Instead, they appear under:
- messages (payload)
- channel parameters (optional schema)
- server variables (optional schema-like constraints)

This changes *where* schemas are referenced, but not the core schema generation logic.

---

## 3. Litestar OpenAPI schema generation patterns to mirror

### 3.1 Generator composition

Litestar’s OpenAPI uses:

- a `TYPE_MAP` for immediate primitive conversions
- a creator/generator class that orchestrates:
  - constrained fields (min/max/pattern/etc.)
  - plugin hooks
  - component schema registration and `$ref` references

The shape is valuable because it keeps:
- quick mappings fast (primitive → schema is O(1))
- complex types composable (plugins can handle their own logic)

### 3.2 Schema registry naming

Litestar’s `SchemaRegistry` uses:

- module + qualname keys
- sanitization of invalid characters
- grouping by model name to shorten prefixes
- collision checks to avoid silently producing invalid specs

We should reuse this idea because AsyncAPI documents will also be heavily component-driven.

---

## 4. Decisions for this phase

### Decision: Keep a dedicated AsyncAPI schema registry

Even if we borrow the algorithm from Litestar OpenAPI, we should not directly import or depend on OpenAPI objects.
AsyncAPI’s component paths differ, and keeping it separate avoids coupling.

### Decision: “Permissive fallback” for unknown types

When generation can’t resolve a type, return an empty schema object rather than failing. This keeps documentation
serving robust in real applications. Future enhancements can add warnings or strict mode.

### Decision: Prefer `oneOf` for unions

Where unions are not “optional” unions, emit `oneOf` with stable ordering for deterministic output.

---

## 5. Test matrix (suggested)

- Primitive mapping: `str`, `int`, `bool`, `float`, `bytes`, `datetime`, `UUID`
- Containers:
  - `list[T]`, `dict[str, T]`
  - nested containers: `list[dict[str, T]]`
- Unions:
  - `T | None`
  - `A | B` with stable ordering
- Models:
  - Pydantic model with optional and required fields
  - attrs class with defaults
  - dataclass with defaults
  - msgspec Struct with rename metadata (if used)
  - TypedDict with required and optional keys
- `$ref` reuse:
  - same model referenced from multiple “messages” yields one component entry
