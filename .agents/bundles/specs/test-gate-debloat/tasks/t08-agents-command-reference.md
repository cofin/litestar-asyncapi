---
type: Task
id: test-gate-debloat:t08
title: Keep one command reference in agent docs
state: completed
priority: P3
verification_strategy: documentation_validation
depends_on: [t07]
files:
  - AGENTS.md
  - .agents/bundles/knowledge/workflow.md
  - .agents/skills/asyncapi-release-ci/SKILL.md
  - .agents/bundles/knowledge/testing/public-seam-tdd.md
  - .agents/bundles/knowledge/testing/distribution-and-browser.md
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
last_verified_commit: 8a4f9db
verification_evidence: "No residual references to test-all, mypy-nocache, no_future_annotations, tools/hooks or anyio markers outside specs/log; make lint 0, make type-check 0, make test 0, make validate-asyncapi 0, make docs 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: 8a4f9db
tags: [docs, agents]
---

# Keep one command reference in agent docs

## Objective

Make `.agents/bundles/knowledge/workflow.md` the single command reference and refresh gate notes made stale by t01-t07.

## Context

- **Why `documentation_validation`.** Prose only.
- `.claude/skills` and `.claude/agents` are symlinks to `.agents/`, so one edit covers both.

## Steps

1. Expand `workflow.md` commands; replace lists in `AGENTS.md`, the release-ci skill and testing knowledge with pointers.
2. Update future-annotations, slotscheck, coverage and anyio notes in gotchas, styleguide, tech stack, checklist and reviewer agent.

## Verification

- **Final:** `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`; `make docs` exits `0`.

## Acceptance Criteria

- [x] `workflow.md` is the only full command list.
- [x] No `.agents` note describes a removed gate or marker.

## Notes & Discoveries

- [2026-11-04 18:38] None.
