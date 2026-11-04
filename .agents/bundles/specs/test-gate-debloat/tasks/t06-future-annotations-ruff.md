---
type: Task
id: test-gate-debloat:t06
title: Ban future annotations with ruff instead of a local hook
state: completed
priority: P2
verification_strategy: static_validation
depends_on: [t05]
files:
  - pyproject.toml
  - .pre-commit-config.yaml
  - tools/hooks/no_future_annotations.py
  - tools/hooks/__init__.py
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
last_verified_commit: 90645df
verification_evidence: "Isolated probe: TID251 flags `import annotations`, `as _ann`, `division, annotations`, after a docstring; ignores `import __future__`, `from __future__ import division`, string literal. Worktree with hook removed: tracked cli.py + untracked _probe.py planted -> make prek exit 2, both files reported TID251; restored -> exit 0; worktree removed. make lint 0, make type-check 0, make test 0, make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: 90645df
tags: [gates, ruff]
---

# Ban future annotations with ruff instead of a local hook

## Objective

Replace `tools/hooks/no_future_annotations.py` with ruff `flake8-tidy-imports.banned-api` for `__future__.annotations`, proven in tracked and untracked files.

## Context

- **Why `static_validation`.** Replacement gate; the charter permits it only on a proven planted violation in both a tracked and an untracked file.
- No file in the repository uses the import, so the ban applies repo-wide (stronger than the hook's `src/litestar_asyncapi/` scope).

## Steps

1. Probe spellings in an isolated ruff project.
2. Add `banned-api`; remove the hook and `tools/hooks/`.
3. In a detached worktree, plant tracked and untracked violations and run `make prek`; restore and rerun.

## Verification

- **Final:** planted `make prek` exit `2` with TID251 on both files; restored exit `0`; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Ruff rejects the import in tracked and untracked files via `make prek`.
- [x] Hook and `tools/hooks/` removed.

## Notes & Discoveries

- [2026-11-04 18:38] `make prek` passes `git ls-files --cached --others --exclude-standard`, so untracked files are in scope.
