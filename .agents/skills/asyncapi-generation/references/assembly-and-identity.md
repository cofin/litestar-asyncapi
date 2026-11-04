---
type: Reference
title: "Assembly & Identity"
description: Assembly & Identity reference for the asyncapi-generation skill.
tags: [skills, asyncapi-generation, assembly-and-identity]
---

# Assembly & Identity

How `src/litestar_asyncapi/asyncapi/generator.py::AsyncAPIGenerator.build_asyncapi` turns discovered channels into a validated document.

## Pipeline

1. `AsyncAPISchemaGenerator(app)` — fresh per build; never share across builds.
2. Root `AsyncAPI(info, asyncapi=config.spec_version, default_content_type=config.default_content_type)`; servers from `AsyncAPIConfig.to_servers`.
3. `deepcopy(config.components)`, then `_merge_components` for `to_operation_traits()` / `to_message_traits()`.
4. `_discover_channels` → `_normalize_channels`.
5. `_populate_channels` (inline `Channel` per key) → `_populate_operations`.
6. `_merge_components(document.components.schemas, schema_generator.components(), "schemas")` — finalize schema names after every `generate` call.
7. `_validate_references(document.to_schema())`.

## Channel normalization

`_normalize_channels` sorts by `(key, provenance)` and raises `ImproperlyConfiguredException` naming both provenances when two channels share a key (for example two handlers on one path). Real discovery never yields two channels for one route, so nothing is merged; `src/tests/integration/conftest.py` asserts unique discovered keys across the integration suite.

## Operation identity

- Default id: `_default_operation_id(channel_key, action)` = `<channel_key>_<action>`.
- `_ensure_unique_operation_id` returns `(candidate_id, map_key)`; the map key is `_sanitize_operation_id` (`[^a-zA-Z0-9_.-]+` → `_`, stripped). Both are compared with `.casefold()` against sets of casefolded used values.
- Collision: `config.strict_uniqueness` → `ImproperlyConfiguredException`; otherwise suffix `_2`, `_3` on id and key.
- The id is not serialized: `Operation` has no `operationId` field. The map key is the identity.

## Messages

- Channel message key: `definition.name` or the operation key, uniquified per channel by `_ensure_unique_message_key` (casefold).
- Same `(channel, name)` declared twice must have identical `_definition_key`; otherwise raise naming both provenances. Unnamed messages are scoped to their operation key (`@<operation_key>`).
- Operation `messages` are `Reference`s to `#/channels/<k>/messages/<m>`, deduped.
- `_build_message`: payload/headers pass through untouched when already `Schema`, `Reference`, `dict`, `bool`, `MultiFormatSchema`; otherwise `schema_generator.generate(value, provenance=...)`.
- Example precedence: explicit `examples` (including `[]`) → `schema_generator.declared_examples` → `generate_example` when enabled. Native DTO payloads never get automatic examples; warn when `create_examples` is on. All examples pass through `utils/examples.py::normalize_examples` with the app's encoders.
- `content_type`: explicit wins; else `_infer_content_type` yields `application/json` only for object/array/ref schemas; otherwise `None`.

## Traits

`_resolve_operation_traits` / `_resolve_message_traits` turn string names into escaped `#/components/{operation,message}Traits/<name>` refs; unknown names raise listing all missing names and pointing at `AsyncAPIConfig.operation_traits` / `message_traits`. Inline trait objects and `Reference`s pass through.

## Determinism

`_definition_key` serializes public values to sorted JSON: types by `module.qualname`, `FieldDefinition` by annotation/name/default/metadata/kwarg, `BaseSchemaObject` by `to_schema()`, dataclasses excluding `provenance` and `route_identity`, bytes as hex. Use it for every ordering and equality comparison between contracts.

## Reference validation

`_reference_index` walks known AsyncAPI and schema positions only (literal `examples`/`default`/`const` data is not traversed). `_validate_references` rejects non-pointer local refs, bad `~` escaping, missing/wrong-kind targets, cycles, channel `servers` not selecting root servers, operation `channel` not selecting a root channel, and operation messages outside the selected channel (through aliases). External refs are not traversed.

## Wire serialization

`src/litestar_asyncapi/spec/base.py::BaseSchemaObject.to_schema`:

- Skip `UNSET`; skip `None` unless `field.metadata["nullable"]` (e.g. `spec/message.py::MessageExample.payload`, `spec/schema.py::Schema.default` / `const`).
- Keys: `metadata["alias"]` (must be `str`) else `_normalize_key` (camelCase, `ref`→`$ref`, `in_`→`in`, `schema_x`→`x` except `schema_format`).
- Values: `_normalize_value` recurses into spec objects, dataclasses, dicts, lists/tuples; enums → `.value`.
- `extensions`: keys must be `str`, start with `x-`, and not collide with modeled keys; otherwise `ValueError`.

## CLI

`src/litestar_asyncapi/cli.py::register_commands` adds `litestar asyncapi export --format json|yaml [--output P] [--overwrite]`, using the plugin's canonical cached accessors. `--output` opens with mode `"x"` unless `--overwrite`; all failures surface as `click.ClickException`. Works with docs routes disabled.

## Canonical tests

| Seam | Test file |
| --- | --- |
| Assembly, ordering, conflicts | `src/tests/unit/test_generator.py`, `test_generator_components.py` |
| Operation id / key uniqueness | `src/tests/unit/test_generator.py` |
| Traits | `src/tests/unit/test_traits.py` |
| Example precedence | `src/tests/unit/extractors/test_example_precedence.py`, `src/tests/integration/test_asyncapi_metadata_examples.py` |
| Wire serialization | `src/tests/unit/spec/test_base.py`, `test_wire_contract.py`, per-model `src/tests/unit/spec/test_*.py` |
| Config contract | `src/tests/unit/test_config.py` |
| Routes / CLI | `src/tests/integration/test_routes.py`, `test_cli.py` |
