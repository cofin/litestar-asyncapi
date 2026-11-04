---
type: Reference
title: "Draft07 Dialect Export"
description: Draft07 Dialect Export reference for the asyncapi-schema skill.
tags: [skills, asyncapi-schema, draft07-dialect]
---

# Draft07 Dialect Export

`src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema` converts Litestar's JSON Schema 2020-12 output into the Draft07 semantics required by native AsyncAPI 3.0/3.1 Schema Objects and official tooling.

## Keyword mapping

| Input (2020-12) | Output (Draft07) | Notes |
| --- | --- | --- |
| `prefixItems: [a, b]` | `items: [a, b]` | Cardinality comes from `minItems`/`maxItems` set by `_SchemaCreator`, never from list length (`test_dialect.py::test_prefix_items_does_not_infer_cardinality`). |
| `prefixItems: []` | omitted | Empty fixed tuples rely on `maxItems: 0`; `items: []` is invalid Draft07. |
| `items` beside non-empty `prefixItems` | `additionalItems` | A list-valued `items` beside `prefixItems` fails. |
| `$defs` | `definitions` | Supplying both fails. Moved `$ref` targets are rewritten by `_Converter.rewrite_references`. |
| `dependentRequired`, `dependentSchemas`, `dependencies` | merged `dependencies` | Overlapping names combine under `allOf` instead of overwriting (`test_dependencies_overlap_without_overwrite`). |
| `$ref` with siblings (implicit modern) | `allOf: [{"$ref": ...}]` plus siblings | Draft07 ignores `$ref` siblings; wrapping keeps constraints (`test_reference_siblings_keep_validation_constraints`). |
| object `discriminator` | dropped | Draft07 has no object discriminator; branches stay (`test_discriminator_branches_and_null_survive`). |

Schema positions traversed: `_SCHEMA_MAPS` (`properties`, `patternProperties`, `definitions`, `$defs`), `_SCHEMA_LISTS` (`allOf`, `anyOf`, `oneOf`), `_SCHEMA_VALUES` (`additionalProperties`, `additionalItems`, `contains`, `propertyNames`, `not`, `if`, `then`, `else`), `items`, `prefixItems`, dependency entries. Every other key is `deepcopy`'d as literal data, so `example`, `examples`, `default`, `const`, `enum` and `x-` extensions keep any `$ref`, `prefixItems` or `$defs` text untouched (`test_only_schema_positions_are_converted`).

## Failure contract

`_fail(path, message)` raises `ImproperlyConfiguredException("Cannot export AsyncAPI Draft07 schema at #/<pointer>: ...")`. Pointer tokens escape `~`→`~0`, `/`→`~1` and percent-encode URI characters (`test_definition_references_escape_uri_tokens`).

Fails on:

- Keywords in `_UNSUPPORTED`: `unevaluatedItems`, `unevaluatedProperties`, `$dynamicRef`, `$dynamicAnchor`, `$recursiveRef`, `$recursiveAnchor`, `$anchor`, `$vocabulary`, `minContains`, `maxContains`, `contentSchema`, `nullable` (`test_unsupported_semantics_report_schema_path`).
- Nested `$id` (`test_nested_resource_ids_are_rejected`).
- Named-anchor `$ref` (`#foo`).
- `$schema` other than Draft07 or 2020-12 (`test_declared_2019_dialect_is_not_reinterpreted_as_2020`), or a nested `$schema` that differs from the root dialect.
- Invalid shapes: non-mapping schema, non-list combinator, non-string `$ref` (`test_invalid_schema_shapes_fail_instead_of_weakening`).

## Declared Draft07 input

When the root declares `$schema: http://json-schema.org/draft-07/schema#`, the converter runs in `legacy` mode: `$ref` siblings keep Draft07 meaning (no `allOf` wrap), and modern keywords (`$defs`, `prefixItems`, `dependentRequired`, `dependentSchemas`) fail instead of being reinterpreted (`test_declared_draft07_preserves_reference_sibling_semantics`, `test_declared_legacy_does_not_reinterpret_modern_annotations`).

## Bypass

`MultiFormatSchema` is returned by `AsyncAPISchemaGenerator.generate` via `to_schema()` without native generation or conversion. `generator.py::_build_message` also passes `Schema`, `Reference`, `dict` and `bool` payloads through unchanged and skips example generation for them (`test_native.py::test_explicit_multiformat_bypasses_native_dialect_conversion`, `test_example_precedence.py::test_explicit_multiformat_payload_does_not_generate_examples`).

## Official gate

`tools/validate_asyncapi.mjs` compiles `@asyncapi/specs` 3.0.0/3.1.0 schemas with AJV and parses fixtures with `@asyncapi/parser`. It masks literal `$ref`/`__proto__` keys only in the parser's disposable input view; the original document is schema-validated unchanged. Run `make validate-asyncapi` (Node (`.nvmrc`)) after any wire-shape change; `make export-asyncapi-fixture` regenerates `.tmp/asyncapi-fixture.json`.
