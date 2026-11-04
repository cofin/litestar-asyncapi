---
type: Task
id: test-gate-debloat:t04
title: Run slotscheck once and require slots on every class
state: completed
priority: P2
verification_strategy: static_validation
depends_on: [t03]
files:
  - .pre-commit-config.yaml
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
last_verified_commit: cc7d99b
verification_evidence: "Planted untracked src/litestar_asyncapi/_slot_probe.py: plain class -> make slotscheck exit 2 'has no slots, but it could have'; slotted-on-unslotted base and overlapping slots -> exit 2; probe removed -> exit 0; make lint 0, make type-check 0, make test 0, make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: cc7d99b
tags: [gates, slotscheck]
---

# Run slotscheck once and require slots on every class

## Objective

Drop the slotscheck prek hook, keep `make slotscheck` and its CI job, and prove the target rejects a planted unslotted class.

## Context

- **Why `static_validation`.** Gate removal needs a planted-violation proof of the remaining gate.
- The hook and target read the same `[tool.slotscheck]` table, so dropping the hook loses nothing.

## Steps

1. Plant violations in an untracked probe module and run `make slotscheck`.
2. Enable `require-subclass` after confirming the tree already passes it.
3. Remove the hook; remove the probe.

## Verification

- **Final:** probe module fails `make slotscheck` (exit 2) with the expected diagnostic; clean tree exits `0`; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] slotscheck prek hook removed; `make slotscheck` and the CI job kept.
- [x] Planted unslotted class fails `make slotscheck`.

## Notes & Discoveries

- [2026-11-04 18:38] With default settings a plain unslotted class passed both the hook and the target (only slotted-on-unslotted-base and overlapping slots fail). `require-subclass = true` already passes on the tree, so it was enabled to make the charter's proof hold; the gate is now stronger than the removed hook.
