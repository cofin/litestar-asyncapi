---
type: Task
id: schema-fixes:t01
title: Keep variadic tuple item types and zero-valued bounds
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/litestar_asyncapi/_compat.py
  - docs/changelog.rst
tests:
  - src/tests/unit/schema_generation/test_native.py
plan_revision: 3
plan_commit: 5f1a5e7
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:59:51Z
last_verified_commit: 5f1a5e7
verification_evidence: "RED: test_constrained_variadic_tuple_keeps_item_type failed (items oneOf [integer, {}]); test_zero_bounds_are_not_dropped failed (KeyError maxItems). GREEN: make lint 0, make type-check 0, make test 0 (223 passed, 93.77%), make validate-asyncapi 0"
created_at: 2026-11-04T17:52:38Z
updated_at: 2026-11-04T17:59:51Z
commit: 89c0796
tags: [schema, tuples, bounds]
---

# Keep variadic tuple item types and zero-valued bounds

## Objective

`Annotated[tuple[int, ...], Parameter(max_items=3)]` exports `items: {type: integer}` with its bounds (audit B4), and zero-valued `min_items`/`max_items`/`min_length`/`max_length` survive for every field, not only fixed tuples (audit B5).

## Context

- **Why `behavior_tdd`.** Both bugs are visible in the schema returned by `AsyncAPISchemaGenerator.generate` and in `components()`.
- **Root causes.** Native `for_collection_constrained_field` builds items from every inner type, including the `Ellipsis` of a variadic tuple, which becomes `oneOf [T, {}]`. Native `_apply_kwarg_definition_metadata` and the constrained-field builders test bounds for truthiness, so `0` is dropped.
- **Fix location.** `_compat.py::_SchemaCreator.for_field_definition` gains a variadic-tuple branch (no plugin claimed) that builds `items` from the first argument and runs `process_schema_result`. `_compat.py::_SchemaCreator.process_schema_result` re-applies zero-valued bounds from the `KwargDefinition`; the fixed-tuple `max_items == 0` special case is removed because the fixed-tuple intersection then sees the zero.
- **Invariants.** Plugin-owned tuples skip local corrections; unconstrained variadic tuples stay unbounded; fixed-tuple bounds still intersect the annotation.
- **Skill:** `asyncapi-schema` (`references/native-bridge.md`).

## Steps

1. **RED.** In `src/tests/unit/schema_generation/test_native.py` add tests for a constrained variadic tuple (direct and `typing.Tuple`) and for zero bounds on `list`, `str` and a dataclass field.
2. **GREEN.** Add the variadic branch and zero-bound re-application in `_compat.py::_SchemaCreator`; drop the fixed-tuple zero special case.
3. **Docs.** Add plain-language lines under Fixed in `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/unit/schema_generation/test_native.py -q --no-cov` fails on the new tests.
- **Final:** `uv run pytest src/tests/unit/schema_generation -q --no-cov`, then `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] Constrained `tuple[T, ...]` exports `items: <T>` with its bounds and never `oneOf [T, {}]`.
- [x] `max_items=0`, `min_items=0`, `max_length=0` and `min_length=0` are exported on every field kind.
- [x] Existing fixed and empty tuple bound tests stay green.
- [x] The changelog records both fixes.

## Notes & Discoveries

- [2026-11-04 17:55] The variadic branch covers every unclaimed `tuple[T, ...]`, not only constrained ones; unconstrained output is unchanged because it matches native `for_object_type`.
- [2026-11-04 17:55] Zero bounds are re-applied in `process_schema_result` before the fixed-tuple intersection, so the old `max_items == 0` special case was deleted.
- [2026-11-04 17:55] Zero `ge`/`le`/`gt`/`lt` already survive on the native constrained-number path (`is not None` checks); they were not changed.
