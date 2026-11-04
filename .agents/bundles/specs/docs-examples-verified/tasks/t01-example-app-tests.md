---
type: Task
id: docs-examples-verified:t01
title: Serve the AsyncAPI document from every docs example in pytest
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/tests/unit/docs/__init__.py
  - src/tests/unit/docs/test_examples.py
  - docs/examples/contracts.py
  - docs/examples/index.rst
tests:
  - src/tests/unit/docs/test_examples.py
plan_revision: 3
plan_commit: f70309e
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T23:10:00Z
last_verified_commit: 1d12cee
verification_evidence: "RED: contracts.py failed with NoRouteMatchFoundException (docs disabled), 10 passed. GREEN: 11 passed. Probe: renaming app in renderers.py fails with AttributeError. make check-all 0 (275 passed, 96.68%). make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum 0 (264 passed, 1 skipped: docs module)."
created_at: 2026-11-04T23:00:00Z
updated_at: 2026-11-04T23:10:00Z
commit: 1d12cee
tags: [docs, examples, testing]
---

# Serve the AsyncAPI document from every docs example in pytest

## Objective

One parametrized test per `docs/examples/**/*.py` module imports its module-level `app`, opens `TestClient(app)`, requests `app.route_reverse("asyncapi:json")` and asserts `200` with `application/vnd.asyncapi+json`.

## Context

- **Why `behavior_tdd`.** New gate with an observable failure on an example that does not serve its document.
- **Invariants.** The installed-wheel lane copies only `src/tests`; the module skips when `docs/examples/` is absent and fails when the glob is empty. No pytest fixtures inside `docs/examples/**`.
- **Canonical tests.** `src/tests/unit/docs/test_examples.py`.

## Steps

1. Write the test (RED) over the example glob, loading each module under a unique `sys.modules` name so dataclass annotations resolve.
2. Make `docs/examples/contracts.py` serve its document (GREEN) by dropping `DocsConfig(enabled=False)`; adjust the gallery prose.
3. Verify the installed-wheel skip.

## Verification

- **Initial:** `uv run pytest src/tests/unit/docs -q --no-cov` fails on `contracts.py`.
- **Final:** the same command, `make check-all` and `make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum` exit `0`.

## Acceptance Criteria

- [x] Every example starts and serves a 3.1.0 document at its reversed `asyncapi:json` route, mounted examples included.
- [x] Removing `app` from an example fails the test.
- [x] The installed-wheel lane skips the module.

## Notes & Discoveries

- [2026-11-04 23:05] `mounted_docs.py` guards its docs with an `authorization: demo-token` header; the test sends it for that module only.
- [2026-11-04 23:05] `contracts.py` disabled its docs routes, so it could not serve a document; the example now serves docs at `/asyncapi/` and the gallery text says so.
