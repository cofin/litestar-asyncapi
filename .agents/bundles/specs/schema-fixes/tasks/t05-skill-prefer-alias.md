---
type: Task
id: schema-fixes:t05
title: Correct the documented prefer_alias default
state: completed
priority: P3
verification_strategy: documentation_validation
depends_on: [schema-fixes:t04]
files:
  - .agents/skills/asyncapi-schema/SKILL.md
  - .agents/skills/asyncapi-schema/references/native-bridge.md
tests:

plan_revision: 3
plan_commit: 5f1a5e7
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:59:51Z
last_verified_commit: 23b8fb5
verification_evidence: "Initial: Litestar([]).plugins.openapi shows PydanticSchemaPlugin prefer_alias=False. Final: make lint 0, make type-check 0, make test 0 (228 passed, 93.91%), make validate-asyncapi 0"
created_at: 2026-11-04T17:52:38Z
updated_at: 2026-11-04T17:59:51Z
commit: a0b359f
tags: [docs, skills]
---

# Correct the documented prefer_alias default

## Objective

The `asyncapi-schema` skill states the real default: Litestar registers `PydanticSchemaPlugin(prefer_alias=False)`, and `True` is only the fallback when no Pydantic plugin is registered.

## Context

- **Why `documentation_validation`.** No behavior changes; the claim is checked against `Litestar([]).plugins.openapi`.
- **Evidence.** `Litestar([]).plugins.openapi` contains `PydanticSchemaPlugin` with `prefer_alias=False`; `_compat.py::create_schema_creator` falls back to `True` only when none is registered.

## Steps

1. Confirm the default with `uv run python -c "from litestar import Litestar; print([getattr(p, 'prefer_alias', None) for p in Litestar([]).plugins.openapi])"`.
2. Correct `.agents/skills/asyncapi-schema/SKILL.md` and `references/native-bridge.md`.
3. Verify with `make lint`.

## Verification

- **Initial:** the command in step 1 prints `False` for the Pydantic plugin while the skill says `True`.
- **Final:** `make lint` exits `0`.

## Acceptance Criteria

- [x] The skill and its native-bridge reference state the `False` default and the `True` fallback.

## Notes & Discoveries

- [2026-11-04 17:59] `.claude/skills/asyncapi-schema` is a hard link to `.agents/skills/asyncapi-schema`, so both copies changed together.
