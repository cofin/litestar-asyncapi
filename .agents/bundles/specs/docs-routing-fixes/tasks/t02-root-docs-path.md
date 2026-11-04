---
type: Task
id: docs-routing-fixes:t02
title: Reject a docs path at the application root
state: completed
priority: P2
verification_strategy: regression_tdd
depends_on: []
files:
  - src/litestar_asyncapi/config.py
  - docs/changelog.rst
tests:
  - src/tests/unit/test_config.py
plan_revision: 3
plan_commit: 91b5852
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:23:00Z
last_verified_commit: 5b8d84c
verification_evidence: "RED: test_docs_path_at_the_application_root_is_rejected['/', '', '//'] failed (no ValueError). GREEN: test_config.py 10 passed; make lint 0, make type-check 0, make test 0 (249 passed, 94.53%), make validate-asyncapi 0"
created_at: 2026-11-04T18:17:00Z
updated_at: 2026-11-04T18:24:00Z
commit: 5b8d84c
tags: [docs-ui, config]
---

# Reject a docs path at the application root

## Objective

`DocsConfig(path=...)` raises `ValueError` when the path normalizes to `/` (`"/"`, `""`, `"//"`), so the docs `/{path:str}` fallback can never become the application's global 404 under the docs guards (audit B12, path part).

## Context

- **Why `regression_tdd`.** Observable at the `DocsConfig` constructor.
- **Fix.** `DocsConfig.__post_init__` checks `litestar.utils.path.normalize_path(self.path) == "/"` before assembling renderers.
- **Canonical test.** `src/tests/unit/test_config.py`.

## Steps

1. **RED.** Parametrized root-path rejection test and a relative `"docs/"` acceptance test.
2. **GREEN.** Guard in `DocsConfig.__post_init__`.
3. Changelog Fixed line.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_config.py -q --no-cov` fails on the three root cases.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `"/"`, `""` and `"//"` raise `ValueError`.
- [x] Non-root paths are accepted unchanged.

## Notes & Discoveries

- [2026-11-04 18:23] The check is unconditional, including `enabled=False` configs mounted under a nested router, as the charter states.
