---
type: Spec
flow_id: schema-fixes
title: Payload Schema Fidelity
description: Keep item types, zero bounds, declared examples and null presence exact in generated payload schemas.
state: completed
parent_prd: contract-fixes
research: []
plan_revision: 3
plan_commit: 5f1a5e7
state_revision: 0
current_task: null
last_verified_checkpoint: a0b359f
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T17:59:51Z
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

## Implementation Plan

- [x] [89c0796] t01 — keep variadic tuple item types and zero-valued bounds (tasks/t01-tuple-and-zero-bounds.md)
- [x] [2875411] t02 — declared examples behind `Optional` and for named payload annotations (tasks/t02-declared-and-resolved-examples.md)
- [x] [b26dfda] t03 — null default recorded only on the outer optional field (tasks/t03-null-presence-on-outer-field.md)
- [x] [23b8fb5] t04 — readable schema errors naming only the failing payload (tasks/t04-schema-error-messages.md)
- [x] [a0b359f] t05 — correct the documented `prefer_alias` default (tasks/t05-skill-prefer-alias.md)

**Recovery checkpoint:** `make lint && make type-check && make test && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **State:** completed. All five tasks landed; `make lint`, `make type-check`, `make test` (228 passed, 93.91%) and `make validate-asyncapi` exit `0` at `a0b359f`.
- **Shared files.** `_compat.py` gained `_SchemaCreator.for_optional_field` and edits inside `process_schema_result`, `for_field_definition` and `declared_schema_examples`; `generator.py` changed one call in `_build_message`. The next chapter edits both files.
- **Discoveries.** A shared enum component no longer receives `default: null` from an optional field; non-null enum defaults remain a backlog item. `.claude/skills/*` are hard links to `.agents/skills/*`.
