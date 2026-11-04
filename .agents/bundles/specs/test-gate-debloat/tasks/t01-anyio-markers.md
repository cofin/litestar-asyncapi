---
type: Task
id: test-gate-debloat:t01
title: Drop unused anyio markers and test dependency
state: completed
priority: P2
verification_strategy: characterization
depends_on: []
files:
  - pyproject.toml
  - uv.lock
tests:
  - src/tests/**/test_*.py
  - src/tests/conftest.py
plan_revision: 3
plan_commit: 5dfa717
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:38:00Z
last_verified_commit: 1c744ad
verification_evidence: "Pass set before 250 == after 250 (diff empty); make lint 0, make type-check 0, make test 0 (250 passed, 94.50%), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: 1c744ad
tags: [debloat, tests]
---

# Drop unused anyio markers and test dependency

## Objective

Remove `pytestmark = pytest.mark.anyio` from every test module, `src/tests/conftest.py::anyio_backend`, and the direct `anyio` entry in the `tests` dependency group.

## Context

- **Why `characterization`.** There are no `async def test` functions, so the marker selects nothing; the collected test count and pass set must stay identical.
- `anyio` is not imported by any test, tool or package module. Litestar still installs it transitively.

## Steps

1. Record the collected pass set (`pytest -rA --no-cov`).
2. Delete the markers and fixture; let ruff remove the now-unused `import pytest` lines.
3. Remove `anyio` from `dependency-groups.tests`; `uv lock`.
4. Re-record the pass set and diff.

## Verification

- **Initial:** `uv run pytest src/tests -q --no-cov -rA` 250 passed.
- **Final:** same 250 node ids pass; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] No `anyio` marker, fixture or direct test dependency remains.
- [x] Collected count and pass set unchanged (250).

## Notes & Discoveries

- [2026-11-04 18:38] The marker sat in 37 test modules plus `conftest.py` (the charter's 40 predates chapter 4's file merges). `uv.lock` drops only the `anyio` group entries.
