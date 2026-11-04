---
type: Task
id: discovery-fixes:t03
title: Merge decorator messages by name in either stacking order
state: completed
priority: P1
verification_strategy: regression_tdd
depends_on: [t01]
files:
  - src/litestar_asyncapi/decorators.py
  - docs/changelog.rst
  - docs/usage/decorators.rst
tests:
  - src/tests/unit/test_decorators.py
plan_revision: 3
plan_commit: 305f2cb
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:22:00Z
last_verified_commit: 3237ed2
verification_evidence: "RED: message-first merge kept only 'Text'; repeated names were replaced instead of raising (4 failed). GREEN: make lint 0, make type-check 0, make test 0 (236 passed, 94.04%), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:22:00Z
commit: 3237ed2
tags: [decorators, messages]
---

# Merge decorator messages by name in either stacking order

## Objective

`asyncapi_operation(messages=...)` and `asyncapi_message` produce the same message set in either stacking order, a repeated message name raises, and the merged `OperationDefinition` is re-validated (audit B8, Master Decision 7).

## Context

- **Why `regression_tdd`.** `messages=` currently replaces messages added by `asyncapi_message` and skips the duplicate-name check; `asyncapi_message` silently replaces a same-name message.
- **Fix.** `decorators.py::asyncapi_operation` and `asyncapi_message` build the merged definition with `dataclasses.replace`, which re-runs `OperationDefinition.__post_init__` (duplicate names raise `ValueError`).
- **Canonical tests.** `src/tests/unit/test_decorators.py`.

## Steps

1. **RED.** Tests for both stacking orders through `build_schema()`, a conflicting name in each order, and `messages=[]` still overriding inference.
2. **GREEN.** Merge by name and rebuild the definition through `replace`.
3. Changelog Fixed line; **verify**.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_decorators.py -q --no-cov` fails on the new tests.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Both stacking orders yield the same messages.
- [x] A repeated message name raises in either order with a message naming it.
- [x] Explicit `messages=[]` still overrides inference.

## Notes & Discoveries

- [2026-11-04 18:20] A repeated message name raises the `ValueError` from `OperationDefinition.__post_init__` re-validation; the unnamed-ambiguity check stays an `ImproperlyConfiguredException`.
- [2026-11-04 18:20] The old test asserting same-name replacement was rewritten to assert the raise; `docs/usage/decorators.rst` was updated.
