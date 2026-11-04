---
type: Task
id: test-gate-debloat:t02
title: Remove constructor echo tests
state: completed
priority: P2
verification_strategy: characterization
depends_on: [t01]
files:
  - src/tests/test_plugin.py
  - src/tests/conftest.py
tests:
  - src/tests/unit/test_config.py
  - src/tests/integration/test_routes.py
plan_revision: 3
plan_commit: 5dfa717
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:38:00Z
last_verified_commit: 8bf6261
verification_evidence: "Pass set 250 -> 246: removed exactly test_plugin.py::{test_plugin_instantiation_with_defaults, test_plugin_instantiation_with_config, test_config_defaults, test_plugin_with_litestar_app}; test_nested_docs_route_configuration[True/False] now passes in integration/test_routes.py; make lint 0, make type-check 0, make test 0 (246 passed, 94.50% unchanged), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:38:00Z
commit: 8bf6261
tags: [debloat, tests]
---

# Remove constructor echo tests

## Objective

Delete the four echo tests in `src/tests/test_plugin.py` and their single-use fixtures after relocating the assertions nothing else covers.

## Context

- **Why `characterization`.** The echo tests repeat constructor inputs. The `title`/`version`/`description`/`servers` default assertions were not covered elsewhere and the nested docs route test is real behavior, so both move first.
- `asyncapi_config`, `asyncapi_plugin` and `app` in `src/tests/conftest.py` had no other consumers, leaving the file empty.

## Steps

1. Add the four default assertions to `unit/test_config.py::test_config_defaults`.
2. Move `test_nested_docs_route_configuration` to `integration/test_routes.py`.
3. Delete `src/tests/test_plugin.py` and `src/tests/conftest.py`.
4. Diff the pass set.

## Verification

- **Initial:** 250 passed.
- **Final:** 246 passed, the difference being exactly the four echo tests; `make lint`, `make type-check`, `make test` and `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Default title, version, description and servers asserted in `test_config_defaults`.
- [x] Nested docs route test lives in `integration/test_routes.py`.
- [x] Pass set shrinks only by the four echo tests; coverage unchanged.

## Notes & Discoveries

- [2026-11-04 18:38] None.
