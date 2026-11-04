---
type: Spec
flow_id: test-gate-debloat
title: Test and Gate Debloat
description: Remove no-op markers, echo tests and duplicated gates, each replaced by an equal or stronger proven check.
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
- Make `.agents/bundles/knowledge/workflow.md` the single command reference. Duplicated command lists in `AGENTS.md`, `.agents/skills/asyncapi-release-ci/**` and `knowledge/testing/**` become pointers to it.

## Public Seams

- `make lint`
- `make check-all`
- `make test`

## Acceptance Boundary

- `make check-all` passes, running the suite once.
- Coverage of `src/litestar_asyncapi` is at or above the post-chapter-5 baseline.
- Every replaced gate has a recorded planted-violation proof in its task notes.
