---
type: Task
id: test-gate-debloat:t07
title: Narrow test per-file-ignores for S101 and PT
state: completed
priority: P3
verification_strategy: static_validation
depends_on: [t06]
files:
  - pyproject.toml
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
last_verified_commit: ce7ac0f
verification_evidence: "With PT unignored only PT018 fires (6, all tests); stdin probe as src/tests/unit/test_probe.py: pytest.raises(ValueError) -> PT011 exit 1, with match= -> exit 0 (PT018 composite assert and bare assert still allowed); make lint 0, make type-check 0, make test 0, make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: ce7ac0f
tags: [gates, ruff]
---

# Narrow test per-file-ignores for S101 and PT

## Objective

Drop `S101` (covered by `S`) and narrow the test `PT` ignore to the codes that fire.

## Context

- **Why `static_validation`.** `PT` was also in the global `ignore`, so a narrower per-file entry would be vacuous; the global entry is removed and tests ignore only `PT018`.

## Steps

1. Remove both PT ignores and list firing codes.
2. Ignore `PT018` in tests only.
3. Prove with a stdin probe under a test filename.

## Verification

- **Final:** `uv run ruff check .` clean; probe PT011 exit `1`; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `S101` removed from test ignores.
- [x] Tests ignore only `PT018`; other PT rules enforced repo-wide.

## Notes & Discoveries

- [2026-11-04 18:38] None.
