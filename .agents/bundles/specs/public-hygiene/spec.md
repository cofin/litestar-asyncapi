---
type: Spec
flow_id: public-hygiene
title: Remove Leaked Internals and Green the Lint Gate
description: Remove internal environment names from tracked files and make make lint pass.
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
tags: [hygiene, release-ci, lint]
---

# Remove Leaked Internals and Green the Lint Gate

## Charter

Remove every tracked mention of the internal environment, keep the author's local setup working through a git-ignored override, and make `make lint` green so later chapters start from a passing gate. Domain skill: `asyncapi-release-ci`.

## Upstream Dependencies

None.

## Key Deliverables

- **`Makefile`:**
  - Delete the OS-detection block that exports `PIP_INDEX_URL`/`UV_INDEX_URL`.
  - Delete the `setup-env` target and its help text, and remove `setup-env` from the prerequisites of `install`.
  - Add `-include Makefile.local` so private overrides load when present.
- **Delete `tools/scripts/setup-env.sh`.** Add `Makefile.local` and `uv.toml` to `.gitignore`. Before relying on that `uv.toml` entry, confirm that no tracked `uv.toml` exists.
- **`.agents/bundles/log.md`:** a one-time redaction of the environment name in the existing entry. This is the only exception to the log's append-only rule.
- **`src/tests/fixtures/asyncapi/README.md`:** remove the stale planning label.
- **`pyproject.toml`:**
  - `tool.codespell.ignore-words-list` gains `addopt`.
  - Remove the `warn_untyped_fields` option that pydantic-mypy rejects.
- **`spec/security_scheme.py`:** remove the inline comment that carries a planning label.

## Public Seams

- `make install`
- `make lint`

## Acceptance Boundary

- `git grep -i` for the environment name returns nothing.
- `make install` on a machine without `Makefile.local` resolves from public PyPI.
- `make lint` and `make type-check` pass.
