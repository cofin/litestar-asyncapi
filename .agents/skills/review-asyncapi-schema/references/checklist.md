---
type: Checklist
title: "SCH Review Checklist"
description: Review rules for the asyncapi-schema domain.
tags: [skills, review-asyncapi-schema, checklist]
---

# SCH Review Checklist

**SCH-01: Private Litestar imports stay in `_compat.py`.**
Why: `litestar._openapi.*` is unstable across the uncapped `>=2.24.0` range; one isolation file keeps breakage reviewable.
Check: grep the diff for `litestar._openapi` or other `litestar._` imports outside `src/litestar_asyncapi/_compat.py`.
Anchor: `src/litestar_asyncapi/_compat.py::create_schema_creator`

**SCH-02: Each generator uses a fresh registry.**
Why: sharing the app OpenAPI registry leaks names and mutates OpenAPI output.
Check: `SchemaRegistry()` constructed per `create_schema_creator` call; no reuse of `app.openapi_schema`, module-level creators or cached registries.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator.__init__`

**SCH-03: App schema plugins and alias preference are honored.**
Why: custom plugins and Pydantic `prefer_alias` define the app's real wire names and shapes.
Check: `plugins=app.plugins.openapi` passed through; `prefer_alias` still read from `PydanticSchemaPlugin`; plugin-owned tuples/Structs skip local corrections (`self.get_plugin_for(...) is None`).
Anchor: `src/litestar_asyncapi/_compat.py::_SchemaCreator.for_field_definition`

**SCH-04: Components finalize once, after all payloads, and refresh earlier outputs.**
Why: early finalization freezes provisional names; skipping the refresh leaves stale `$ref` strings.
Check: no new `generate_components_schemas()` call before `components()`; every dict returned by `generate()` is recorded in `_outputs`; `build_asyncapi` calls `components()` after `_populate_operations`.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator.components`

**SCH-05: Fixed tuple bounds come from the annotation.**
Why: Draft07 `items` arrays do not limit length; only `minItems`/`maxItems` do.
Check: tuple changes keep `min_items = max(len(args), declared)` and `max_items = min(len(args), declared)`; variadic `tuple[X, ...]` stays unbounded; nothing infers length from `prefixItems` in the dialect.
Anchor: `src/litestar_asyncapi/_compat.py::_SchemaCreator.for_field_definition`

**SCH-06: Empty fixed tuple exports `maxItems: 0`.**
Why: `items: []` is invalid Draft07, and a dropped zero bound accepts any array.
Check: `tuple[()]` and explicit `max_items=0` still yield `maxItems: 0`; dialect omits empty `prefixItems` rather than emitting `items: []`.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::_Converter.keyword`

**SCH-07: Array-like msgspec Structs follow wire order.**
Why: `array_like=True` encodes positional arrays in `encode_name` order with the tag first.
Check: positions use `msgspec.inspect.type_info` field order; `minItems` = last required index + 1 (+ tag); `maxItems` set only with `forbid_unknown_fields`; `properties`/`required` cleared.
Anchor: `src/litestar_asyncapi/_compat.py::_SchemaCreator.for_plugin`

**SCH-08: Dialect conversion traverses schema positions only.**
Why: literal `example`, `examples`, `default`, `const`, `enum` and `x-` data may legitimately contain `$ref`, `prefixItems` or `$defs` text.
Check: new keywords are added to `_SCHEMA_MAPS`/`_SCHEMA_LISTS`/`_SCHEMA_VALUES` only when they hold subschemas; literals reach the `deepcopy` branch.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::_Converter.keyword`

**SCH-09: Unsupported semantics fail with a JSON pointer.**
Why: silently dropping a constraint weakens the published contract.
Check: removals from `_UNSUPPORTED` come with a lossless Draft07 translation and test; new failure paths call `_fail(path, ...)`; no `try/except` that swallows `ImproperlyConfiguredException`.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::_fail`

**SCH-10: `$ref` siblings and moved targets stay correct.**
Why: Draft07 ignores `$ref` siblings; `$defs`→`definitions` moves targets.
Check: implicit-modern `$ref` with siblings wraps into `allOf`; declared Draft07 does not; `rewrite_references` runs after conversion; pointer tokens escape `~0`/`~1` and URI characters.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::_Converter.rewrite_references`

**SCH-11: Declared dialects are not reinterpreted.**
Why: a declared Draft07 or unknown dialect has different keyword meaning.
Check: legacy mode still rejects `$defs`/`prefixItems`/`dependent*`; mixed nested `$schema` fails; only Draft07 and 2020-12 URIs accepted; nested `$id` rejected.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema`

**SCH-12: Explicit null presence survives export.**
Why: `default: null`/`const: null` is a different contract from an absent keyword.
Check: `process_schema_result` still records field and `schema_extra` null default/const; `normalize_native_schema` emits `None` only for tracked fields and keeps null dict entries; `spec/schema.py` nullable fields keep `UNSET` defaults.
Anchor: `src/litestar_asyncapi/_compat.py::normalize_native_schema`

**SCH-13: Explicit schemas bypass generation and examples.**
Why: `MultiFormatSchema`, `Schema`, `Reference`, `dict` and `bool` payloads are user-authored contracts, not annotations.
Check: `generate()` returns `MultiFormatSchema.to_schema()` before conversion; `_build_message` passthrough tuples include all explicit types; no example generation for them.
Anchor: `src/litestar_asyncapi/asyncapi/generator.py::_build_message`

**SCH-14: Example precedence and isolation hold.**
Why: explicit `[]`/null examples are user intent; shared RNG reseeding changes other app factories.
Check: order is explicit > `declared_examples` > `generate_example`; `config.create_examples` gates generation; `native_example_value` keeps a private `Random()`/`Faker` and `__set_as_default_factory_for_type__=False`; unsupported generation warns and returns `UNSET`.
Anchor: `src/litestar_asyncapi/asyncapi/utils/examples.py::generate_example`

**SCH-15: Errors carry payload and provenance context.**
Why: users must locate the failing handler or channel.
Check: new exception paths inside `generate()`/`components()` are covered by the wrapped exception tuple and include `provenance`/`_origins`; `resolve_annotation` names the unresolved string.
Anchor: `src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator.generate`

**SCH-16: Tests assert wire output through public seams.**
Why: private-state assertions pass while the exported document regresses.
Check: new tests live in `test_native.py`, `test_dialect.py` or `test_examples.py`, call `AsyncAPISchemaGenerator`/`to_asyncapi_schema`/`generate_example` with a real `Litestar` app, and assert exported dicts or exception text; wire changes refresh the fixture and pass `make validate-asyncapi`; Python follows PEP 604/585, Google docstrings and no inline comments.
Anchor: `src/tests/unit/schema_generation/test_native.py`

## Optional declared examples

Outer FieldDefinition examples take priority over non-null optional member examples. Verify emitted messages with automatic generation both enabled and disabled. Explicit Schema references address final Draft07 wire keys; do not apply native dialect reference rewriting to constructor conveniences.
