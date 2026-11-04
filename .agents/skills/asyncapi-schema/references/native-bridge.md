---
type: Reference
title: "Native Bridge, Registry and Examples"
description: Native Bridge, Registry and Examples reference for the asyncapi-schema skill.
tags: [skills, asyncapi-schema, native-bridge]
---

# Native Bridge, Registry and Examples

How `src/litestar_asyncapi/_compat.py` and `asyncapi/schema_generation/schema.py` reuse Litestar's schema engine while keeping AsyncAPI wire fidelity.

## Registry lifecycle

`_compat.py::create_schema_creator` constructs `_SchemaCreator` with:

- `plugins=app.plugins.openapi`: app schema plugins participate even with OpenAPI disabled (`test_native.py::test_application_plugin_works_with_openapi_disabled_and_preserves_literals`).
- `schema_registry=SchemaRegistry()`: fresh per generator; `test_native.py::test_generation_registry_is_independent_from_application_openapi` guards isolation.
- `prefer_alias` read from the app's `PydanticSchemaPlugin`, which Litestar registers with `prefer_alias=False`; the `True` fallback applies only without a Pydantic plugin; `test_examples.py::test_generated_decimal_uuid_and_pydantic_aliases` covers both values.
- `generate_examples=False`: examples are produced separately by `asyncapi/utils/examples.py`.
- `signature_namespace=app.signature_namespace`: resolves string and forward references.

`schema.py::AsyncAPISchemaGenerator.generate` records each `(native, output)` pair. `components()` calls `schema_registry.generate_components_schemas()` (which finalizes short names), then re-exports every recorded native schema and mutates the earlier output dict in place, so references handed out before a later same-name registration stay correct (`test_native.py::test_same_short_names_update_early_references`). `generator.py::AsyncAPIGenerator.build_asyncapi` calls `components()` exactly once, after discovery and operation population.

Anti-pattern: calling `schema_registry.generate_components_schemas()` early (for example to read examples). `declared_schema_examples` resolves through `get_schema_for_field_definition` specifically to avoid freezing provisional names.

## `_SchemaCreator` corrections

| Override | Correction | Guarding test |
| --- | --- | --- |
| `for_field_definition` | Fixed tuples: `prefix_items` + `min_items`/`max_items` from `len(args)`, intersected with declared bounds; `tuple[()]` and `max_items=0` keep `maxItems: 0`; skipped when a plugin owns the type. | `test_nested_and_empty_tuple_cardinality`, `test_tuple_bounds_intersect_annotation_constraints`, `test_tuple_zero_maximum_is_not_dropped` |
| `for_field_definition` | Forward refs resolve against the owning module namespace (pushed by `for_plugin`) plus the app signature namespace without mutating globals. | `test_unresolved_nested_local_forward_reference_has_context` |
| `for_plugin` | `array_like` msgspec Structs become positional arrays in `encode_name` order, tag first; `minItems` from last required field; `maxItems` only with `forbid_unknown_fields`. | `test_array_like_struct_uses_wire_order_and_accepts_default_tail`, `test_array_like_struct_can_forbid_extra_items`, `test_array_like_required_position_after_default` |
| `process_schema_result` | Records explicit `None` default/const (field default or `schema_extra`) in `null_fields` keyed by `id(schema)`; `_null_schemas` keeps those objects alive so ids stay unique. | `test_explicit_field_default_null_differs_from_absent_default`, `test_explicit_schema_extra_null_preserves_presence` |

`normalize_native_schema` serializes native spec objects using alias metadata and `_normalize_key`, honors `_exclude_fields`, keeps null-valued dict entries, and emits `None` only for fields listed in `null_fields`. Bare native `Schema(default=None)` cannot reveal explicit presence; only the tracked paths can.

## DTO payloads

`_compat.py::websocket_payload` wraps DTO-backed fields in `NativeDTOPayload`; `generate()` calls its `create_schema(creator)`, which delegates to the DTO's public `create_openapi_schema`. `generator.py::_build_message` skips automatic examples for `NativeDTOPayload` and warns instead, because the transferred shape differs from the annotation.

## Examples

Order in `generator.py::_build_message`:

1. `definition.examples` when not `None` (an explicit `[]` suppresses generation; `test_example_precedence.py::test_explicit_empty_examples_prevent_generation`).
2. `AsyncAPISchemaGenerator.declared_examples` → native `examples`/`example`, then Pydantic `json_schema_extra["examples"]`.
3. `examples.py::generate_example` when `config.create_examples` is true: kwarg default → field default → first enum → `native_example_value`.

`native_example_value` subclasses `ExampleFactory` with a private `Random()` and seeded-per-instance `Faker`, `__set_as_default_factory_for_type__=False`, so shared factories and process RNG are untouched (`test_examples.py::test_generation_does_not_mutate_shared_random_state`). Direct constraints on a `KwargDefinition` raise inside `_check_constraints` because the native factory does not enforce them; the failure becomes a warning and `UNSET` (`test_unchecked_direct_constraints_omit_automatic_example`). Recursive required models likewise warn and omit.

`normalize_examples` wraps raw values in `MessageExample` and JSON round-trips payload/headers with `get_serializer(app.type_encoders)`, preserving `name`/`summary` and explicit null payloads (`test_examples_use_application_encoders_and_preserve_metadata`, `test_explicit_null_message_example_is_preserved`).

## Error context

`AsyncAPISchemaGenerator.generate` converts `ImproperlyConfiguredException`, `NameError`, `TypeError`, `ValueError` into `ImproperlyConfiguredException("Cannot generate AsyncAPI payload ... for <provenance>: ...")`. `components()` wraps export failures with the list of payload origins. `resolve_annotation` raises `TypeError` for unresolved string annotations. Tests: `test_unsupported_native_output_has_payload_and_handler_context`, `test_unresolved_namespace_has_payload_and_handler_context`.

## Optional example precedence

declared_schema_examples reads the outer FieldDefinition schema before descending into a single non-null member. Otherwise Parameter(examples=...) on int | None disappears. Keep the public document regression in test_example_precedence.py. native_example_value imports ExampleFactory lazily so basic package import does not require Pydantic.
