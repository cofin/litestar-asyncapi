---
type: Task
id: discovery-fixes:t04
title: Normalize operation actions and validate spec_version
state: completed
priority: P1
verification_strategy: regression_tdd
depends_on: [t03]
files:
  - src/litestar_asyncapi/asyncapi/datastructures.py
  - src/litestar_asyncapi/decorators.py
  - src/litestar_asyncapi/config.py
  - docs/changelog.rst
tests:
  - src/tests/unit/extractors/test_datastructures.py
  - src/tests/unit/test_config.py
  - src/tests/unit/test_decorators.py
plan_revision: 3
plan_commit: 305f2cb
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:30:00Z
last_verified_commit: e164cd9
verification_evidence: "RED: OperationDefinition(action=' Send ') raised; three unsupported spec_version values were accepted (4 failed). The decorator action test passed before and after, pinning behavior across the _coerce_action deletion. GREEN: make lint 0, make type-check 0, make test 0 (241 passed, 94.15%), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:30:00Z
commit: e164cd9
tags: [validation, config, contracts]
---

# Normalize operation actions and validate spec_version

## Objective

`OperationDefinition(action=" Send ")` normalizes like the decorators already do, `decorators.py::_coerce_action` is deleted, and `AsyncAPIConfig(spec_version="3.0")` is rejected (audit B12 action and spec_version, Master Decision 8). The `DocsConfig.path` part of B12 belongs to `docs-routing-fixes`.

## Context

- **Why `regression_tdd`.** Constructing the public contract types reproduces both defects.
- **Fix.** `datastructures.py::OperationDefinition.__post_init__` applies `.strip().lower()` to string actions and raises `ValueError` naming the accepted values; decorators normalize through it. `config.py::AsyncAPIConfig.__post_init__` checks `{"3.0.0", "3.1.0"}`.
- **Canonical tests.** `unit/extractors/test_datastructures.py`, `unit/test_config.py`, `unit/test_decorators.py`.

## Steps

1. **RED.** Tests for mixed-case/padded actions, an invalid action message, and an unsupported `spec_version`.
2. **GREEN.** Normalize in `__post_init__`, delete `_coerce_action`, validate `spec_version`.
3. Changelog Fixed line; **verify**.

## Verification

- **Initial:** `uv run pytest src/tests/unit/extractors/test_datastructures.py src/tests/unit/test_config.py -q --no-cov` fails on the new tests.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `OperationDefinition` accepts `" Send "` as `OperationAction.SEND` and rejects unknown actions with a clear message.
- [x] `_coerce_action` is deleted; decorators keep eager action validation.
- [x] `AsyncAPIConfig` rejects unsupported `spec_version` values.

## Notes & Discoveries

- [2026-11-04 18:28] `DocsConfig(path="/")` is left to `docs-routing-fixes` as chartered.
