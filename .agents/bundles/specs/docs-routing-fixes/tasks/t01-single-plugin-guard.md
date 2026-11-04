---
type: Task
id: docs-routing-fixes:t01
title: Reject a second AsyncAPIPlugin on one application
state: completed
priority: P1
verification_strategy: regression_tdd
depends_on: []
files:
  - src/litestar_asyncapi/plugins/core.py
  - docs/changelog.rst
tests:
  - src/tests/integration/test_routes.py
plan_revision: 3
plan_commit: 91b5852
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:22:00Z
last_verified_commit: 3defa63
verification_evidence: "RED: test_second_plugin_in_one_app_is_rejected_at_startup[True/False] failed (no exception). GREEN: test_routes.py 11 passed; make lint 0, make type-check 0, make test 0 (245 passed, 94.52%), make validate-asyncapi 0"
created_at: 2026-11-04T18:17:00Z
updated_at: 2026-11-04T18:23:00Z
commit: 3defa63
tags: [docs-ui, routing, security]
---

# Reject a second AsyncAPIPlugin on one application

## Objective

`Litestar(plugins=[AsyncAPIPlugin(...), AsyncAPIPlugin(...)])` raises `ImproperlyConfiguredException` at construction, naming both docs paths, whether or not either plugin has docs enabled (audit B3, Master Decision 2). A single plugin alongside other plugins is unaffected.

## Context

- **Why `regression_tdd`.** Fixed route names (`asyncapi:json`, `asyncapi:assets`) let `url_for` on one docs page resolve to the other plugin's routes, exposing a guarded document.
- **Fix.** `AsyncAPIPlugin.on_app_init` scans `app_config.plugins` for another `AsyncAPIPlugin` (`plugin is not self`) before mounting the docs router.
- **Canonical test.** `src/tests/integration/test_routes.py`.

## Steps

1. **RED.** Parametrized two-plugin construction test (`enabled` True/False) and a single-plugin-with-`PydanticPlugin` test.
2. **GREEN.** Guard in `on_app_init`; docstring `Raises:` section.
3. Changelog Fixed line.

## Verification

- **Initial:** `uv run pytest src/tests/integration/test_routes.py -q --no-cov` fails on the two-plugin cases.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Two plugins in one app fail at startup with a message naming both docs paths.
- [x] The guard fires with docs disabled on either plugin.
- [x] One plugin among other plugins starts and serves `/asyncapi/asyncapi.json`.

## Notes & Discoveries

- [2026-11-04 18:22] `ruff format` collapsed the `next(...)` generator onto two lines; prek reported the rewrite as a failure on the first `make lint`, the second run exited 0.
