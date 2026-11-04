---
type: Pattern
title: AsyncAPI 3.x Schema Generation Patterns
description: Draft07 wire semantics, Parameter objects, operation-map identity and example normalization for generated documents.
tags: [patterns, schema, asyncapi, tuples, operation-id]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: dialect
    resource: src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema
    title: Draft07 dialect adapter
  - id: uniq
    resource: src/litestar_asyncapi/asyncapi/generator.py::_ensure_unique_operation_id
    title: Operation-map identity
  - id: ptr
    resource: src/litestar_asyncapi/asyncapi/generator.py::_json_pointer_escape
    title: JSON Pointer escaping
  - id: param
    resource: src/litestar_asyncapi/spec/channel.py::Parameter
    title: AsyncAPI 3 Parameter object
  - id: ex
    resource: src/litestar_asyncapi/asyncapi/utils/examples.py::normalize_examples
    title: Example normalization
  - id: alias
    resource: src/litestar_asyncapi/_compat.py::create_schema_creator
    title: Alias preference bridge
---

# AsyncAPI 3.x Schema Generation Patterns

<!-- truth: start -->
- Wire tuples are Draft07 `items` arrays with `minItems`/`maxItems` derived from the Python annotation; never infer exact length from `prefixItems` alone.
- Empty fixed tuples emit `maxItems: 0`, never `items: []`.
- `Parameter` objects carry no nested schema; type information goes in `description`.
- Operation identity is the operations-map key, deduplicated with `.casefold()`; `strict_uniqueness=True` raises `ImproperlyConfiguredException`; no wire `operationId` property.
- Internal `$ref` tokens escape `~`→`~0`, `/`→`~1`, then percent-encode.
- Examples round-trip through the application's Litestar type encoders; explicit examples (including `[]` and `None`) win over generated ones.
<!-- truth: end -->

## 1. Draft07 tuple fidelity

Litestar may use `prefixItems` internally. Native AsyncAPI 3.0/3.1 uses Draft07 `items` arrays for positional tuples, with explicit `minItems`/`maxItems` for fixed Python tuple length. Variadic tuples use one `items` schema[^dialect].

The dialect adapter translates only schema positions and preserves example/default/const literal data. The native compatibility adapter derives fixed tuple bounds from the annotation. Unsupported semantic keywords fail with a schema path rather than weaken validation. Explicit `MultiFormatSchema` values bypass native conversion.

Anti-pattern: emitting `prefixItems` on the wire. Reason: official `@asyncapi/specs` Draft07 validation and the React renderer ignore it, silently dropping positional types.

## 2. AsyncAPI 3 Parameter objects

AsyncAPI 3 `Parameter` objects do not contain a nested `Schema`[^param]. Fields are limited to `description`, `enum`, `default`, `examples`, `location` and `x-` extensions. Extractors place the Python type in `description`.

## 3. Case-insensitive operation-map identity

`_ensure_unique_operation_id` checks both the candidate identity and its sanitized map key with `.casefold()` against everything already registered[^uniq]:

```python
candidate_fold = candidate.casefold()
key_fold = key.casefold()
if not (candidate_fold in used_ids or key_fold in used_keys):
    return candidate, key
if config.strict_uniqueness:
    raise ImproperlyConfiguredException(msg)
suffix += 1
candidate = f"{base_id}_{suffix}"
```

Without strict mode, suffixes start at `_2`. Message keys use the same rule through `_ensure_unique_message_key`.

## 4. RFC 6901 JSON Pointer escaping

```python
def _json_pointer_escape(segment: str) -> str:
    return quote(segment.replace("~", "~0").replace("/", "~1"), safe="~")
```

RFC 6901 escaping runs first; percent-encoding then makes parameterized addresses such as `/ws/{room_id}` valid URI fragments[^ptr].

## 5. Example normalization and alias preference

Explicit message examples (including empty lists and null) precede declared examples and optional generation. `normalize_examples` round-trips payloads and headers through `get_serializer(app.type_encoders)` and wraps them in `MessageExample`[^ex]. Do not reseed shared native factories or process RNGs. Explicit schemas are not Python annotations and bypass automatic example generation. Omit unsupported constrained or recursive automatic examples with a warning rather than inventing a value.

Initialize the native `SchemaCreator` alias preference from the active `PydanticSchemaPlugin` configuration[^alias]; native defaults otherwise diverge from application serialization. Cover `prefer_alias=False` and `True`. msgspec wire aliases are preserved independently.

[^dialect]: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema`
[^uniq]: `src/litestar_asyncapi/asyncapi/generator.py::_ensure_unique_operation_id`
[^ptr]: `src/litestar_asyncapi/asyncapi/generator.py::_json_pointer_escape`
[^param]: `src/litestar_asyncapi/spec/channel.py::Parameter`
[^ex]: `src/litestar_asyncapi/asyncapi/utils/examples.py::normalize_examples`
[^alias]: `src/litestar_asyncapi/_compat.py::create_schema_creator`
