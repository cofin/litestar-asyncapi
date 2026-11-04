---
type: Suppressions
title: "SCH False-Positive Suppressions"
description: Intentional asyncapi-schema patterns reviewers must not flag.
tags: [skills, review-asyncapi-schema, false-positive-suppressions]
---

# SCH False-Positive Suppressions

Intentional repository patterns that look suspicious in isolation.

**FP-SCH-01: Private `litestar._openapi` imports in `_compat.py`.**
`_compat.py` imports `SchemaRegistry`, `SchemaCreator`, `ExampleFactory`, `_create_field_meta` and `StructSchemaPlugin` from private modules by design; it is the single isolation seam guarded by the 2.24.0 and latest CI lanes.
DO NOT FLAG private imports inside `src/litestar_asyncapi/_compat.py`.

**FP-SCH-02: Subclassing native `SchemaCreator` instead of writing a mapper.**
`_SchemaCreator` overrides three methods to correct tuple, array-like Struct and null-presence output while delegating all other type evaluation to Litestar.
DO NOT FLAG the inheritance or calls to `super()` as coupling; a parallel type mapper is the rejected alternative.

**FP-SCH-03: `prefixItems` on internal native `Schema` objects.**
`_SchemaCreator` and `spec/schema.py::Schema.prefix_items` use `prefix_items` internally; `to_asyncapi_schema` converts it to Draft07 `items` on export.
DO NOT FLAG `prefix_items`/`prefixItems` in internal schema construction; flag only if it reaches the exported wire document.

**FP-SCH-04: Output dicts mutated in place by `components()`.**
`AsyncAPISchemaGenerator.components` calls `output.clear(); output.update(converted)` on dicts previously returned by `generate()` so early references match finalized names.
DO NOT FLAG this as surprising aliasing or request a copy; copying breaks `test_same_short_names_update_early_references`.

**FP-SCH-05: `id(schema)`-keyed `null_fields` plus `_null_schemas`.**
Null presence is tracked by object identity; `_null_schemas` holds references so ids are not reused during the build.
DO NOT FLAG `_null_schemas` as unused or the id keys as fragile.

**FP-SCH-06: Dropping object `discriminator` and `dependency` keywords in the main loop.**
`_Converter.convert` skips mapping-valued `discriminator` (no Draft07 equivalent; `oneOf` branches carry the contract) and defers `dependencies`/`dependentRequired`/`dependentSchemas` to `_Converter.dependencies`, which merges them.
DO NOT FLAG these `continue` branches as lost data.

**FP-SCH-07: Broad exception tuples that warn and return `UNSET` in `generate_example`.**
Automatic examples are optional; `ParameterException`, `TypeError`, `ValueError`, `RecursionError` and `NameError` become a warning and omission so documentation still builds. `_check_constraints` raises deliberately to route constrained fields there.
DO NOT FLAG as swallowed errors; schema generation errors are not handled this way.

**FP-SCH-08: Local `ExampleFactory` subclass with a fresh `Random()` and `Faker` per call.**
`native_example_value` builds an isolated factory to avoid reseeding shared polyfactory/Faker state.
DO NOT FLAG per-call construction as wasteful or suggest a module-level shared factory.

**FP-SCH-09: Default `Litestar([])` when no app is supplied.**
`AsyncAPISchemaGenerator.__init__` and `generate_example` construct an empty app for direct use and tests; the plugin path always passes the real app.
DO NOT FLAG as hidden global state or a missing dependency injection.
