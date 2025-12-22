# PRD-002: AsyncAPI Schema Generation

**Parent PRD**: `specs/active/asyncapi-plugin/prd.md`
**Document Version**: 1.0
**Created**: 2025-12-17
**Status**: COMPLETE
**Dependencies**: PRD-001 (spec foundation)

---

## Intelligence Context

### Similar Implementations (Pattern References)

- `litestar/_openapi/schema_generation/schema.py` - schema creator, TYPE_MAP, plugin hooks, constrained fields
- `litestar/_openapi/datastructures.py` - schema registry and `$ref` path generation
- `litestar/typing.py` (`FieldDefinition`) - type introspection strategy and metadata transport

### Patterns to Follow

- Central generator class that:
  - receives an introspected `FieldDefinition`
  - emits a spec `Schema` object (or `$ref`) deterministically
- A schema registry to cache and deduplicate repeated schemas
- Plugin-based type handlers for “framework-specific” models (Pydantic, dataclass, msgspec, TypedDict)
- Conservative defaults: generate valid schema even when metadata is incomplete

---

## 1. Problem Statement

AsyncAPI documents need reusable, consistent JSON Schema payload definitions for message bodies (and optionally headers).
The plugin must generate these schemas from Python types used in websocket handlers and ChannelsPlugin channel payloads.

We want the generated schema quality to match Litestar OpenAPI’s behavior: stable component keys, `$ref` reuse, and
support for common Python modeling libraries.

---

## 2. Goals / Non-Goals

### Goals

1. Convert Python type annotations into AsyncAPI `Schema` spec objects.
2. Support key model sources:
   - Pydantic models
   - attrs classes
   - dataclasses
   - msgspec Structs
   - TypedDict
   - built-in primitives, containers, unions, literals
3. Deduplicate schemas with `$ref` and generate a components map for PRD-004.
4. Provide extension points so downstream integrations can register schema plugins.

### Non-Goals

- No websocket route extraction (PRD-003).
- No assembly of AsyncAPI documents (PRD-004).
- No validation against the official AsyncAPI JSON schema in this phase (defer to PRD-004).

---

## 3. Acceptance Criteria

1. **AC-201: Primitive and container coverage**
   - Basic types (`str`, `int`, `float`, `bool`, `bytes`, `dict`, `list`, etc.) map to correct schema shape.
2. **AC-202: Model support**
   - Pydantic model types produce object schemas with properties and required fields.
   - attrs classes produce equivalent object schemas.
   - Dataclasses and msgspec Structs produce equivalent object schemas.
   - TypedDict produces object schemas.
3. **AC-203: Unions and optionals**
   - `T | None` yields nullable/union semantics consistently.
   - Multi-type unions generate `oneOf` (or equivalent draft-07 approach) deterministically.
4. **AC-204: `$ref` reuse**
   - Repeated model types are emitted as `$ref` references and collected into `components.schemas`.
5. **AC-205: Testing**
   - 90%+ coverage for schema generation modules.

---

## 4. Technical Approach

### 4.1 Module Layout

```
src/litestar_asyncapi/_asyncapi/
  __init__.py
  datastructures.py          # AsyncAPIContext, SchemaRegistry, caches
  schema_generation/
    __init__.py
    schema.py                # AsyncAPISchemaGenerator
    utils.py                 # helpers (typing, constraints, naming)
    plugins/
      __init__.py
      pydantic.py
      attrs.py
      dataclass.py
      msgspec.py
      typed_dict.py
```

### 4.2 Generator API (proposed)

The generator should be usable by extractors (PRD-003) and the document generator (PRD-004):

- `generate_schema(field_definition: FieldDefinition) -> Schema | Reference`
- `get_schema_name(field_definition) -> str` (or via registry)
- `register_plugin(plugin)` for type-specific support

Important: do not leak Litestar OpenAPI objects; generate AsyncAPI spec `Schema` objects from PRD-001.

### 4.3 Schema Registry Strategy

Copy the spirit of Litestar’s `SchemaRegistry`:

- Compute stable keys for types: `(<module parts...>, <qualname>)` with sanitization.
- Maintain a mapping:
  - type key → registered schema
  - reference id → registered schema (for reverse lookup / path rewriting)
- Generate `components.schemas` by:
  - grouping by model name
  - shortening keys by removing common prefixes
  - rewriting reference paths to match final names

### 4.4 Handling “unknown” types

When the generator cannot introspect a type meaningfully:
- return a permissive schema (empty schema object) to keep generation robust
- optionally record warnings (future enhancement)

---

## 5. Testing Strategy

### Unit Tests

- Primitive mappings (table-driven tests)
- Container types: list/tuple/set/dict, nested generics
- Union/Literal handling
- Model schemas for:
  - Pydantic BaseModel
  - dataclass
  - msgspec Struct
  - TypedDict
- Registry behavior:
  - stable key generation
  - `$ref` reuse
  - name collision resolution

### Integration Test (lightweight)

Generate schemas for the same model used in multiple contexts and assert it becomes a single schema component with
multiple references.

---

## 6. Deliverables

- `src/litestar_asyncapi/_asyncapi/schema_generation/` implementation
- Schema registry and `$ref` strategy for AsyncAPI components
- Tests covering major type sources
