---
type: Spec
flow_id: schema-fixes
title: Payload Schema Fidelity
description: Keep item types, zero bounds, declared examples and null presence exact in generated payload schemas.
state: draft
parent_prd: contract-fixes
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [schema, draft07, examples]
---

# Payload Schema Fidelity

## Charter

Fix the generated payload schemas that silently weaken or contradict the Python annotation (audit B4, B5, B9, B10, B11), and make schema error messages readable. Domain skill: `asyncapi-schema`. Review with `review-asyncapi-schema`.

## Upstream Dependencies

- `public-hygiene`.

## Key Deliverables

- **B4.** Add a variadic-tuple branch to `_compat.py::_SchemaCreator.for_field_definition`: `tuple[T, ...]` with kwarg bounds becomes `items: <T>` with those bounds, and never `oneOf [T, {}]`.
- **B5.** `_SchemaCreator.process_schema_result` re-applies zero-valued `min_*`/`max_*` bounds from the `KwargDefinition` for every field. The fixed-tuple special case is folded into it.
- **B9.** `_compat.py::declared_schema_examples` unwraps a single-member `Optional` before reading declared examples.
- **B10.** `generator.py::_build_message` resolves string payload annotations with `resolve_annotation(..., app)` before generating examples.
- **B11.** Null presence is recorded only on the outer field, so union members no longer carry `default: null`.
- **Error messages.** `asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator` errors use `error.detail` and a short annotation repr, and name only the payload origin that failed.
- **Skill doc.** Correct the `prefer_alias` default in `.agents/skills/asyncapi-schema/SKILL.md`. Litestar registers `PydanticSchemaPlugin(prefer_alias=False)`.

## Public Seams

`AsyncAPISchemaGenerator` and the generated `components/schemas` and message `examples`. Tests go in `src/tests/unit/schema_generation/test_native.py` and `test_example_precedence.py`.

## Acceptance Boundary

Each of B4, B5, B9, B10 and B11 has a test that failed before its fix, and `make validate-asyncapi` still passes.
