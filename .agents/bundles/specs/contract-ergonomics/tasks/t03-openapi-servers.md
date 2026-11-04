---
type: Task
id: contract-ergonomics:t03
title: Opt-in WebSocket servers derived from OpenAPI servers
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [t02]
files:
  - docs/integrations/security-and-servers.md
  - docs/learn/installation.md
  - docs/project/changelog.md
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/asyncapi/openapi.py
  - src/litestar_asyncapi/config.py
  - src/tests/fixtures/apps/openapi.py
  - src/tests/fixtures/asyncapi/README.md
  - src/tests/fixtures/asyncapi/openapi-3.0.0.json
  - src/tests/fixtures/asyncapi/openapi-3.1.0.json
tests:
  - src/tests/unit/test_openapi_inheritance.py
plan_revision: 2
plan_commit: 36294c1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T02:40:00Z
last_verified_commit: 7b911dd
verification_evidence: "RED: 4 new tests failed (inherit_openapi_servers unknown). GREEN: focused file green. make lint 0, make type-check 0, make test 0 (307 passed, 96.98%), make validate-asyncapi 0 (24 documents; openapi fixtures carry wss and templated ws servers bound to /ping), make docs 0"
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T02:40:00Z
commit: 7b911dd
tags: [feature, openapi, servers, tdd]
---

# Opt-in WebSocket servers derived from OpenAPI servers

## Objective

With `inherit_openapi_servers=True`, absolute OpenAPI server URLs become AsyncAPI servers (`http`→`ws`, `https`→`wss`, host, pathname, variables and description carried over) bound only to WebSocket-sourced channels; relative URLs are skipped (R3).

## Context

- **Why `behavior_tdd`.** New `servers` entries and channel `servers` references.
- **Invariants.** Off by default, because channels without `servers` belong to every server. A host is never invented. Derived servers are named `openapi`, `openapi_2`, …; a name colliding with a different configured server raises naming both sources. Channels that already list servers keep them.
- **Canonical tests.** `src/tests/unit/test_openapi_inheritance.py`.

## Steps

1. Write failing tests (RED): http/https/relative URLs, variables, default off, binding only to WebSocket channels, collision.
2. Implement (GREEN) `config.py::AsyncAPIConfig.inherit_openapi_servers`, `asyncapi/openapi.py::inherited_servers`, binding in `generator.py::_populate_channels`.
3. Add a derived server to the `openapi-*` fixtures; run gates.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_openapi_inheritance.py -q --no-cov` fails (no derived servers).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi`, `make docs` exit `0`.

## Acceptance Criteria

- [x] R3: opt-in, absolute URLs only, protocol mapping, variables, bound only to WebSocket channels.
- [x] R8: the derived server validates for 3.0.0 and 3.1.0.

## Notes & Discoveries

- [2026-11-05 02:15] Non-http(s) absolute URLs are skipped like relative ones; no warning, since Litestar's default `/` server is always present.
- [2026-11-05 02:20] Server-name collisions raise only when the configured server differs (`Conflicting server 'openapi': AsyncAPIConfig.servers and OpenAPIConfig.servers (inherited)`).
- [2026-11-05 02:25] The servers sentence in the security page and installation page landed here.
