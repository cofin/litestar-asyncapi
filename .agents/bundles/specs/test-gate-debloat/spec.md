---
type: Spec
flow_id: test-gate-debloat
title: Test and Gate Debloat
description: Remove no-op markers, echo tests and duplicated gates, each replaced by an equal or stronger proven check.
state: completed
parent_prd: contract-fixes
research: []
plan_revision: 3
plan_commit: 5dfa717
state_revision: 0
current_task: null
last_verified_checkpoint: 8a4f9db
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T18:40:00Z
tags: [debloat, tests, gates, release-ci]
---

# Test and Gate Debloat

## Charter

Shrink the test and gate surface without weakening any check, following `flow:debloat` and its `references/test-and-gate-debloat.md`. This chapter runs after chapters 2–5 so it does not churn files they rewrite. Domain skill: `asyncapi-release-ci`.

## Upstream Dependencies

- `wire-contract-fixes`, `schema-fixes`, `discovery-fixes`, `docs-routing-fixes`.

## Key Deliverables

Each item is one of the Master ledger rows assigned to chapter 6.

- Delete `pytestmark = pytest.mark.anyio` from the 40 test files and remove `conftest.py::anyio_backend`. Drop the `anyio` test dependency if nothing else imports it. The collected test count and the set of passing tests must not change.
- Delete the four echo tests in `src/tests/test_plugin.py` and their single-use fixtures. First move the default assertions they make that are not covered elsewhere (`title`, `version`, `description`, `servers`) into `unit/test_config.py::test_config_defaults`, and move `test_nested_docs_route_configuration` into `integration/test_routes.py`.
- Keep `make slotscheck` and its CI job, and drop the prek hook. Prove that a planted unslotted class fails `make slotscheck`.
- Rework `make check-all` so the suite runs once. Remove the `test-all` and `pre-commit` aliases, and keep only one of the identical `mypy`/`mypy-nocache` targets. Update `.github/workflows/*.yml` and docs references to match.
- Replace `tools/hooks/no_future_annotations.py` with ruff `flake8-tidy-imports.banned-api` only if ruff rejects a planted `from __future__ import annotations` in both a tracked and an untracked file. Otherwise keep the hook and add a self-test.
- In the test `per-file-ignores`, drop `S101` and narrow `PT` to the codes that actually fire.
- Set `[tool.coverage.run] concurrency = ["multiprocessing", "thread"]` so handlers run in the `TestClient` worker thread are measured, and record the new coverage baseline. Total coverage may rise.
- Make `.agents/bundles/knowledge/workflow.md` the single command reference. Duplicated command lists in `AGENTS.md`, `.agents/skills/asyncapi-release-ci/**` and `knowledge/testing/**` become pointers to it.

## Public Seams

- `make lint`
- `make check-all`
- `make test`

## Acceptance Boundary

- `make check-all` passes, running the suite once.
- Coverage of `src/litestar_asyncapi` is at or above the post-chapter-5 baseline.
- Every replaced gate has a recorded planted-violation proof in its task notes.

## Implementation Plan

- [x] [1c744ad] t01 — drop unused anyio markers and test dependency (tasks/t01-anyio-markers.md)
- [x] [8bf6261] t02 — remove constructor echo tests (tasks/t02-echo-tests.md)
- [x] [a14f451] t03 — measure coverage in TestClient handler threads (tasks/t03-coverage-threads.md)
- [x] [cc7d99b] t04 — run slotscheck once and require slots on every class (tasks/t04-slotscheck-once.md)
- [x] [9c0529f] t05 — run the test suite once in check-all (tasks/t05-check-all-once.md)
- [x] [90645df] t06 — ban future annotations with ruff instead of a local hook (tasks/t06-future-annotations-ruff.md)
- [x] [ce7ac0f] t07 — narrow test per-file-ignores for S101 and PT (tasks/t07-ruff-test-ignores.md)
- [x] [8a4f9db] t08 — keep one command reference in agent docs (tasks/t08-agents-command-reference.md)

**Recovery checkpoint:** `make check-all && make type-check && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **State:** completed. `make check-all` (one test run: 246 passed, 96.53%), `make lint`, `make type-check`, `make test`, `make validate-asyncapi` and `make docs` exit `0` at `8a4f9db`.
- **Baseline:** 250 tests, 94.50% before; 246 tests, 96.53% after. The four removed tests are the `test_plugin.py` echo tests; the rise is the thread-concurrency measurement fix (`docs.py` 46% -> 94%, `plugins/core.py` 94% -> 100%, `plugins/renderers.py` 69% -> 97%).
- **Discoveries:**
  - The anyio marker was in 37 test modules plus `conftest.py`, not 40.
  - Default slotscheck accepts a plain unslotted class; `require-subclass` was enabled (tree already compliant) so the planted-class proof holds.
  - `PT` was also ignored globally, so the global entry was removed; tests ignore only `PT018`.
  - The future-annotations ban is now repo-wide through ruff TID251, proven on tracked and untracked files via `make prek`.
