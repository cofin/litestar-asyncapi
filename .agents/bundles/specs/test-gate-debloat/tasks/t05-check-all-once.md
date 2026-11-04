---
type: Task
id: test-gate-debloat:t05
title: Run the test suite once in check-all
state: completed
priority: P2
verification_strategy: static_validation
depends_on: [t04]
files:
  - Makefile
  - docs/contribution-guide.rst
tests: []
plan_revision: 3
plan_commit: 5dfa717
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:38:00Z
last_verified_commit: 9c0529f
verification_evidence: "make -n check-all: pytest invocations 2 (old Makefile) -> 1; make check-all exit 0 with one pytest summary (246 passed, 96.53%); make type-check 0, make validate-asyncapi 0; no workflow referenced the removed targets"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: 9c0529f
tags: [gates, makefile]
---

# Run the test suite once in check-all

## Objective

`check-all` runs lint and then the coverage-gated suite once; remove the `test-all` and `pre-commit` aliases and the duplicate `mypy-nocache` target.

## Context

- **Why `static_validation`.** Target composition only; the suite and its coverage floor are unchanged.
- `make test` already writes term, HTML and XML reports through `addopts`; `make coverage` stays as the standalone xdist report target.

## Steps

1. Count pytest invocations with `make -n check-all` against the old and new Makefile.
2. Edit targets and the contribution guide.
3. Run `make check-all`.

## Verification

- **Final:** `make check-all` exits `0` with one test run; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `check-all` runs the suite once.
- [x] `test-all`, `pre-commit` and `mypy-nocache` removed; `mypy` kept.
- [x] Workflows and docs reference no removed target.

## Notes & Discoveries

- [2026-11-04 18:38] None.
