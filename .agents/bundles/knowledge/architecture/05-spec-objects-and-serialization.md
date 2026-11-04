---
type: Guide
title: "Architecture 05: Spec Objects & Serialization"
description: Slotted dataclass representations of AsyncAPI 3.x entities and BaseSchemaObject recursive serialization.
tags: [architecture, spec-objects, serialization, slots, asyncapi-3]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: base
    resource: src/litestar_asyncapi/spec/base.py::BaseSchemaObject
    title: Recursive wire serialization
  - id: core
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin
    title: Application-encoder normalization
  - id: ex
    resource: src/litestar_asyncapi/asyncapi/utils/examples.py::normalize_examples
    title: Example normalization
---

# Architecture 05: Spec Objects & Serialization

All AsyncAPI entities are modeled as strongly-typed slotted dataclasses inheriting from `BaseSchemaObject`.

## Object Hierarchy

```
BaseSchemaObject (__slots__ = ())
       ▲
       ├── AsyncAPI (@dataclass(slots=True))
       ├── Info, Contact, License
       ├── Server, ServerVariable
       ├── Channel, Parameter
       ├── Operation, OperationTrait
       ├── Message, MessageTrait
       ├── Components
       ├── Schema (@dataclass(slots=True))
       └── Reference (@dataclass(slots=True))
```

## `BaseSchemaObject` Serialization Contract

The base class provides uniform serialization via `to_schema()`:[^base]
1. **Omission and null:** `UNSET` is Litestar's native `Empty` sentinel and omits nullable schema fields such as `default` and `const`; explicit `None` remains JSON null for fields marked nullable. Ordinary optional model fields use `None` for omission. Arbitrary dictionaries preserve null-valued entries.
2. **CamelCase Key Normalization:** Python attributes such as `default_content_type` use AsyncAPI camelCase keys such as `defaultContentType`. Native tuple export uses Draft07 `items` arrays.
3. **Alias Overrides:** Fields declaring `metadata={"alias": "..."}` use explicit wire keys (e.g. `ref` serializes as `"$ref"`).
4. **Recursive Conversion:** Nested `BaseSchemaObject` instances and collections are converted recursively to pure Python primitives.

## AsyncAPI 3.x Compliance Details

- **Parameter Entity:** In AsyncAPI 3.0, `Parameter` does not accept a nested `schema` object. It accepts only:
  - `description: str | None`
  - `enum: list[str] | None`
  - `default: str | None`
  - `examples: list[str] | None`
  - `location: str | None`
  - `extensions: dict[str, Any]`
- Extractor logic sets the descriptive Python type string in `description`.

- The document defaults to 3.1.0 and supports explicit 3.0.0. Operation identity is its operations-map key; do not emit an `operationId` property.
- Security requirements contain SecurityScheme objects or references, not OpenAPI requirement-name maps.
- Common `extensions` must use `x-` keys and cannot overwrite modeled fields. Preserve extension null literals.
- Native payload schemas use the implemented Draft07 adapter around Litestar schema generation. Retain the AsyncAPI-specific serializer because native OpenAPI model serialization loses required null presence and AsyncAPI aliases.
- Application type encoders apply through one native round trip, `decode_json(encode_json(value, serializer=get_serializer(app.type_encoders)))`: `AsyncAPIPlugin` runs it over `document.to_schema()` for the cached canonical schema[^core], and `normalize_examples` runs it per example payload and headers[^ex]. Scalar and null values survive.
- Native model plugins own optional model support.

[^base]: `src/litestar_asyncapi/spec/base.py::BaseSchemaObject`
[^core]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin`
[^ex]: `src/litestar_asyncapi/asyncapi/utils/examples.py::normalize_examples`
