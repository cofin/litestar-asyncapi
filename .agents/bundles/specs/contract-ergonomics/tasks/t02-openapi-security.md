---
type: Task
id: contract-ergonomics:t02
title: Inherit OpenAPI security schemes through one adapter
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [t01]
files:
  - Makefile
  - docs/project/changelog.md
  - pyproject.toml
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/asyncapi/openapi.py
  - src/litestar_asyncapi/config.py
  - src/tests/fixtures/apps/openapi.py
  - src/tests/fixtures/asyncapi/README.md
  - src/tests/fixtures/asyncapi/openapi-3.0.0.json
  - src/tests/fixtures/asyncapi/openapi-3.1.0.json
  - uv.lock
tests:
  - src/tests/integration/test_cli.py
  - src/tests/unit/test_openapi_inheritance.py
plan_revision: 2
plan_commit: 36294c1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T02:00:00Z
last_verified_commit: 7c6e515
verification_evidence: "RED: 15 new tests failed (no securitySchemes). GREEN: focused file green. make lint 0, make type-check 0, make test 0 (303 passed, 96.95%), make validate-asyncapi 0 (24 documents incl. openapi-3.0.0/3.1.0), make docs 0. Negative check: the raw JWTAuth shape (scheme Bearer + name) is rejected by the official schema."
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T02:00:00Z
commit: 7c6e515
tags: [feature, openapi, security, tdd]
---

# Inherit OpenAPI security schemes through one adapter

## Objective

OpenAPI security scheme definitions (including those registered by Litestar auth backends into a `components` list) appear under `components.securitySchemes` using the research mapping table; unmappable schemes and relative OAuth flows are skipped with a warning; a name colliding with a different configured scheme raises naming both sources; every mapped type validates under the official 3.0.0 and 3.1.0 schemas (R2, R8).

## Context

- **Why `behavior_tdd`.** New components in the generated document.
- **Mapping (binding).** `http`+bearer → `http`, `scheme: bearer` lowercased, `name`/`in` dropped; other `http` → `http` with its scheme; `apiKey` header/query/cookie → `httpApiKey`; `oauth2` → `oauth2` with `availableScopes` always present, flows with relative URLs skipped with a warning; `openIdConnect` as-is; `mutualTLS` → `X509`; anything else skipped with a warning. Requirements are never inherited.
- **Invariants.** Components lists are merged without mutating the config (later entries win, as in Litestar). Real `JWTAuth` registration is used in tests, which needs the `jwt` extra in the test dependency group.
- **Canonical tests.** `src/tests/unit/test_openapi_inheritance.py`; fixture drift in `src/tests/integration/test_cli.py::test_committed_generated_fixtures_match_export`.

## Steps

1. Write failing tests (RED): each mapping, JWTAuth-registered list components, relative OAuth URLs and unmappable types warn, collision raises, identical configured scheme accepted, `inherit_openapi=False`.
2. Implement (GREEN) `asyncapi/openapi.py::inherited_security_schemes` and its merge in `generator.py::AsyncAPIGenerator.build_asyncapi`.
3. Add `tests/fixtures/apps/openapi.py` with 3.0.0 and 3.1.0 apps, export targets in `Makefile::export-asyncapi-fixture`, committed fixtures and README note.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_openapi_inheritance.py -q --no-cov` fails (no `securitySchemes`).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi`, `make docs` exit `0`.

## Acceptance Criteria

- [x] R2: mapping table, warnings on skips, no requirements, collision error naming both sources.
- [x] R8: the `openapi-*` fixtures with every mapped scheme validate for 3.0.0 and 3.1.0.

## Notes & Discoveries

- [2026-11-05 01:10] `pyjwt` was not installed, so the `jwt` extra was added to the `tests` dependency group (`litestar[standard,attrs,pydantic,jwt]`, lock adds pyjwt and cryptography). Tests and the fixture use real `JWTAuth` registration, which appends to a `components` list.
- [2026-11-05 01:20] Non-bearer `http` schemes are also lowercased (RFC 7235 scheme names are case-insensitive); `NonBearerHTTPSecurityScheme` forbids `bearerFormat`, so it is emitted only for bearer.
- [2026-11-05 01:25] Any relative OAuth URL (authorization, token or refresh) skips that flow; an `oauth2` scheme with no surviving flow is skipped as unmappable. OpenAPI `Reference` entries and `apiKey`/`http` without the needed fields are unmappable.
- [2026-11-05 01:30] Collisions reuse `_merge_components` with a `source` label: `Conflicting component securitySchemes/<name>: AsyncAPIConfig.components and OpenAPIConfig.components (inherited)`; identical converted definitions are accepted.
