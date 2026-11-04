---
name: asyncapi-schema
description: Use when changing payload/header schema generation or message examples in litestar-asyncapi — _compat.py (_SchemaCreator, create_schema_creator, normalize_native_schema, native_example_value), schema_generation/schema.py (AsyncAPISchemaGenerator), schema_generation/dialect.py (to_asyncapi_schema), utils/examples.py, spec/schema.py (Schema, MultiFormatSchema) — or when fixing tuple bounds, null presence, recursion, aliases, Draft07 export or official-validator failures.
---

# AsyncAPI Schema Generation

<!-- truth: start -->
- Litestar's native `SchemaCreator` evaluates Python types; this domain owns only narrow wire corrections and the Draft07 export. Never reimplement type mapping.
- Every private `litestar._openapi.*` import lives in `src/litestar_asyncapi/_compat.py`. Other modules import from `_compat`, never from `litestar._openapi`.
- Each `AsyncAPISchemaGenerator` builds a fresh `SchemaRegistry` via `create_schema_creator(app)`; never share the app's OpenAPI registry or cache.
- App schema plugins (`app.plugins.openapi`) participate even when OpenAPI serving is disabled; user plugins override native tuple/Struct shapes.
- `prefer_alias` comes from the app's `PydanticSchemaPlugin`, which Litestar registers with `prefer_alias=False`; `True` applies only when no Pydantic plugin is registered. msgspec `encode_name` aliases stay native.
- `generate()` returns provisional dicts; `components()` finalizes native names and refreshes every previously returned dict in place. Call it once, after all payloads, before serializing.
- Native AsyncAPI 3.0/3.1 schemas are Draft07: fixed tuples export `items` arrays plus `minItems`/`maxItems` derived from the annotation. `prefixItems` alone never implies exact length.
- Empty fixed tuple `tuple[()]` exports `maxItems: 0`, never `items: []`. Tuple bounds intersect declared constraints; variadic tuples stay unbounded.
- Array-like msgspec Structs export wire-ordered positional `items` (tag first); `minItems` = last required position (+tag); `maxItems` only with `forbid_unknown_fields`.
- The dialect adapter traverses schema positions only. `examples`, `example`, `default`, `const`, `enum` and `x-` extensions are copied as literal data.
- Unsupported semantics (`unevaluated*`, `$dynamicRef`, `$anchor`, nested `$id`, mixed or unknown `$schema`, `nullable`) raise `ImproperlyConfiguredException` with a JSON pointer path. Never silently drop a constraint.
- Implicit 2020-12 `$ref` with siblings becomes `allOf: [{$ref}]` to keep constraints; declared Draft07 keeps its own `$ref` semantics.
- Explicit `MultiFormatSchema`, `Schema`, `Reference`, `dict` and `bool` payloads bypass native generation and dialect conversion.
- Explicit `None` default/const (field default or `schema_extra`) survives as JSON null via `null_fields`; absent stays absent.
- Failures name the payload and its provenance (handler/channel) in `ImproperlyConfiguredException`.
- Example precedence: explicit message examples (including `[]` and `None` payload) > declared schema/model examples > generated example. Generated examples never reseed shared RNG/Faker and are omitted with a warning when unsupported.
- `normalize_examples` round-trips through `encode_json`/`decode_json` with `app.type_encoders`.
- Python >=3.10, PEP 604/585 typing, Google docstrings, zero inline comments, `__slots__` on owned classes.
- Litestar dependency is `>=2.24.0` with no upper cap; CI exercises 2.24.0 and latest `<3`.
<!-- truth: end -->

## Scope

- `src/litestar_asyncapi/_compat.py`: `_SchemaCreator`, `create_schema_creator`, `resolve_annotation`, `normalize_native_schema`, `declared_schema_examples`, `native_example_value`, `NativeDTOPayload`.
- `src/litestar_asyncapi/asyncapi/schema_generation/schema.py`: `AsyncAPISchemaGenerator` (`generate`, `components`, `declared_examples`).
- `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py`: `to_asyncapi_schema`, `_Converter`.
- `src/litestar_asyncapi/asyncapi/utils/examples.py`: `generate_example`, `normalize_examples`.
- `src/litestar_asyncapi/spec/schema.py`: `Schema`, `MultiFormatSchema`.
- Consumer: `src/litestar_asyncapi/asyncapi/generator.py::_build_message` and `AsyncAPIGenerator.build_asyncapi` (calls `components()` once and merges via `_merge_components`).
- Tests: `src/tests/unit/schema_generation/test_native.py`, `test_dialect.py`, `src/tests/unit/utils/test_examples.py`, `src/tests/unit/extractors/test_example_generation.py`, `test_example_precedence.py`. Official gate: `tools/validate_asyncapi.mjs`.

## Seams

| Role | Element |
| --- | --- |
| Module | `AsyncAPISchemaGenerator`: small interface (`generate`, `components`, `declared_examples`) hiding native registry, null tracking and dialect export. |
| Interface | `generate(type_or_field, *, provenance) -> dict | bool`; `components() -> dict[str, Any]`. |
| Implementation | `_SchemaCreator` overrides (`for_field_definition`, `for_plugin`, `process_schema_result`) plus `normalize_native_schema`. |
| Seam | `_compat.py` is the only file allowed to touch `litestar._openapi`; `to_asyncapi_schema` is the pure Draft07 boundary. |
| Adapter | `_Converter` (2020-12 → Draft07), `NativeDTOPayload` (defers DTO `create_openapi_schema`), `native_example_value` (isolated `ExampleFactory`). |

Dependency categories:

- **In-process**: `to_asyncapi_schema`, `normalize_native_schema`, `_SchemaCreator` — test directly with real inputs.
- **Local-substitutable**: a real `Litestar([...], plugins=[...])` app supplies plugins, signature namespace and encoders; build one per test instead of mocking.
- **Remote-owned**: Litestar private schema internals (`SchemaRegistry`, `SchemaCreator`, `ExampleFactory`) — reached only through `_compat.py`; guarded by the 2.24.0/latest CI lanes.
- **External boundary**: `@asyncapi/specs`, `@asyncapi/parser`, AJV in `tools/validate_asyncapi.mjs` — exercised by `make validate-asyncapi`, never mocked in Python tests.

## Workflow

1. Classify the change: native bridge (`_compat.py`), registry/finalization (`schema.py`), Draft07 export (`dialect.py`) or examples (`examples.py`). Read the matching reference below.
2. Write the failing behavior test in the canonical file (`test_native.py`, `test_dialect.py` or `test_examples.py`) through `AsyncAPISchemaGenerator` or `to_asyncapi_schema`; assert the exported wire dict, not private state.
3. Run it red: `uv run pytest <test path> -q --no-cov`.
4. Make the smallest correction in the owning file. Prefer configuring native behavior over adding a parallel mapping; keep new private imports inside `_compat.py`.
5. For export changes, assert both the converted keyword and that literal data and `$ref` targets are unchanged.
6. For failures, assert `ImproperlyConfiguredException` text includes the JSON pointer or payload provenance.
7. Run the focused file green, then the domain suite, then the gates below.
8. If wire output changed, refresh the fixture with `make export-asyncapi-fixture` and run `make validate-asyncapi`.

## Verification

```bash
uv run pytest src/tests/unit/schema_generation -q --no-cov
uv run pytest src/tests/unit/utils/test_examples.py src/tests/unit/extractors/test_example_precedence.py -q --no-cov
make type-check
make slotscheck
make lint
make test
make validate-asyncapi
```

Focused runs need `--no-cov`: the global `--cov-fail-under=80` addopt makes partial runs exit 1. `make validate-asyncapi` requires Node (`.nvmrc`) and `make js-install`.

## References

- [Native bridge, registry and examples](references/native-bridge.md)
- [Draft07 dialect export](references/draft07-dialect.md)
- [Architecture 04: Schema generation](../../bundles/knowledge/architecture/04-schema-generation.md)
- [Schema generation patterns](../../bundles/knowledge/patterns/schema-generation.md)
- [ADR-002: Draft07 wire dialect](../../bundles/knowledge/decisions/adr-002-draft07-wire-dialect.md)
- [AsyncAPI contracts glossary](../../bundles/knowledge/domains/asyncapi-contracts.md)
- [Public-seam TDD](../../bundles/knowledge/testing/public-seam-tdd.md)
- [Runtime and tooling gotchas](../../bundles/knowledge/gotchas/runtime-and-tooling.md)
