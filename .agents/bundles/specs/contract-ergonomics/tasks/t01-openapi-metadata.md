---
type: Task
id: contract-ergonomics:t01
title: Inherit document metadata from the application's OpenAPI config
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - docs/project/changelog.md
  - docs/project/migration.md
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/asyncapi/openapi.py
  - src/litestar_asyncapi/config.py
tests:
  - src/tests/integration/test_plugin_cache.py
  - src/tests/unit/test_config.py
  - src/tests/unit/test_openapi_inheritance.py
plan_revision: 2
plan_commit: 36294c1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T01:00:00Z
last_verified_commit: d2b8cd5
verification_evidence: "RED: 5 of 6 new tests failed (title stayed AsyncAPI, inherit_openapi unknown). GREEN: focused file green. make lint 0, make type-check 0, make test 0 (284 passed, 96.87%), make validate-asyncapi 0 (22 documents), make docs 0"
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T01:00:00Z
commit: d2b8cd5
tags: [feature, openapi, metadata, tdd]
---

# Inherit document metadata from the application's OpenAPI config

## Objective

Unset `AsyncAPIConfig` metadata (`title`, `version`, `description`, `contact`, `license`, `terms_of_service`, `external_docs`) is filled from `app.openapi_config` at build time; explicit values win; `inherit_openapi=False` disables inheritance; tags are never inherited (R1, R4).

## Context

- **Why `behavior_tdd`.** New observable `info` values in the generated document.
- **Invariants.** ADR-001: Litestar OpenAPI types are converted in one adapter module (`asyncapi/openapi.py`) and never stored on `AsyncAPIConfig`. `app.openapi_config` is read lazily inside `AsyncAPIGenerator.build_asyncapi`; `None` is handled; the config is never mutated and `app.openapi_schema` / `to_openapi_schema()` are never called. `License.identifier` and `summary` have no AsyncAPI `Info` equivalent and are dropped. Without an OpenAPI config the fallbacks stay `AsyncAPI` / `1.0.0`.
- **Canonical tests.** `src/tests/unit/test_openapi_inheritance.py` (new adapter seam) through `AsyncAPIGenerator.build_schema` and `AsyncAPIPlugin.get_asyncapi_schema`; config defaults in `src/tests/unit/test_config.py`.

## Steps

1. Write failing tests (RED): inherited title/version/description/contact/license/terms/external docs; explicit values win; `inherit_openapi=False`; `openapi_config=None`; tags absent; config not mutated.
2. Implement (GREEN) `config.py::AsyncAPIConfig` optional metadata fields and `inherit_openapi`, `asyncapi/openapi.py::inherited_info`, and the call in `generator.py::AsyncAPIGenerator.build_asyncapi`.
3. Update tests that relied on the `AsyncAPI` default title; refactor and run gates.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_openapi_inheritance.py -q --no-cov` fails (title stays `AsyncAPI`).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi`, `make docs` exit `0`.

## Acceptance Criteria

- [x] R1: unset metadata comes from OpenAPI; explicit values win; tags are not inherited; `inherit_openapi=False` disables it.
- [x] R4: lazy read, `openapi_config=None` handled, no mutation, no `openapi_schema`.

## Notes & Discoveries

- [2026-11-05 00:40] `AsyncAPIConfig.title`/`version` became `str | None`; the generator falls back to `AsyncAPI`/`1.0.0` only when no OpenAPI config is available or inheritance is off. `Litestar()` always has a default `OpenAPIConfig(title="Litestar API")`, so the default title changes for every app that does not set one; existing cache tests were updated to `Litestar API`.
- [2026-11-05 00:45] A non-mutation check comparing the whole `OpenAPIConfig.__dict__` to a deepcopy fails on render-plugin identity, so the test compares the inheritable fields instead.
- [2026-11-05 00:50] Changelog (Changed: default title, breaking; Added: inheritance) and migration note landed with this task rather than t05.
