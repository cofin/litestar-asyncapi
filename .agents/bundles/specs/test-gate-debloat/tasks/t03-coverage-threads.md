---
type: Task
id: test-gate-debloat:t03
title: Measure coverage in TestClient handler threads
state: completed
priority: P2
verification_strategy: static_validation
depends_on: [t02]
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
last_verified_commit: a14f451
verification_evidence: "coverage 7.16.2 (py3.10 venv) and 7.17.1 (py3.12 isolated probe) accept concurrency=[multiprocessing, thread]; docs.py 46%->94%, plugins/core.py 94%->100%, plugins/renderers.py 69%->97%; total 94.50%->96.53%; xdist run 96.53%; make lint 0, make type-check 0, make test 0 (246 passed), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: a14f451
tags: [coverage, tooling]
---

# Measure coverage in TestClient handler threads

## Objective

Set `[tool.coverage.run] concurrency = ["multiprocessing", "thread"]` so handlers run in the `TestClient` worker thread are traced.

## Context

- **Why `static_validation`.** A measurement fix with no behavior change; total coverage may rise.
- Added to this chapter's deliverables at execution time (discovery recorded by `docs-routing-fixes`).

## Steps

1. Confirm both locked coverage versions accept the combination.
2. Change the setting.
3. Compare per-file coverage.

## Verification

- **Initial:** `make test` 94.50% (`docs.py` 46%).
- **Final:** `make test` 96.53% (`docs.py` 94%); `uv run pytest src/tests -n auto` 96.53%; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `thread` is traced alongside `multiprocessing`.
- [x] New baseline recorded: 96.53% total.

## Notes & Discoveries

- [2026-11-04 18:38] Probe for coverage 7.17.1 ran in an isolated scratch directory with a one-thread script (100%), then was deleted.
