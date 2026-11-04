---
type: Task
id: schema-fixes:t03
title: Record explicit null defaults only on the outer optional field
state: completed
priority: P2
verification_strategy: behavior_tdd
depends_on: [schema-fixes:t02]
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
last_verified_commit: 2875411
verification_evidence: "RED: integer member carried default: null. GREEN: make lint 0, make type-check 0, make test 0 (226 passed, 93.80%), make validate-asyncapi 0"
created_at: 2026-11-04T17:52:38Z
updated_at: 2026-11-04T17:59:51Z
commit: b26dfda
tags: [schema, null]
---

# Record explicit null defaults only on the outer optional field

## Objective

`x: Optional[int] = None` exports `default: null` on the outer `oneOf` only; the integer member no longer carries a contradictory `default: null` (audit B11).

## Context

- **Why `behavior_tdd`.** Visible in `components()` output.
- **Root cause.** Native `for_optional_field` builds the non-optional member with the field's default, so `_SchemaCreator.process_schema_result` records null presence on the member too.
- **Fix location.** `_compat.py::_SchemaCreator.for_optional_field` passes a copy of the field without its `None` default to the native method. The outer field still records the null default in `for_field_definition`. Non-null defaults are untouched.
- **Invariant.** Explicit null default/const survives; absent stays absent.

## Steps

1. **RED.** In `src/tests/unit/schema_generation/test_native.py` assert that an optional field with a `None` default keeps `default: null` on the outer schema and none on its non-null member.
2. **GREEN.** Override `for_optional_field` in `_compat.py::_SchemaCreator`.
3. **Docs.** Add a plain-language line under Fixed in `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/unit/schema_generation/test_native.py -q --no-cov` fails on the new test.
- **Final:** `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] Union members no longer carry `default: null`.
- [x] The outer optional field keeps `default: null`; existing null-presence tests stay green.
- [x] The changelog records the fix.

## Notes & Discoveries

- [2026-11-04 17:58] `for_optional_field` passes `replace(field, default=Empty)` only when the default is `None`; non-null defaults keep native behavior.
- [2026-11-04 17:58] Side effect: a shared enum component no longer receives `default: null` from an optional field with a `None` default. Non-null enum defaults (the backlog item) are unchanged.
