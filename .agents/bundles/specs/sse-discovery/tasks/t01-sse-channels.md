---
type: Task
id: sse-discovery:t01
title: Discover Server-Sent Event routes as send-only channels
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/litestar_asyncapi/asyncapi/extractors/sse.py
  - src/litestar_asyncapi/asyncapi/extractors/__init__.py
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/config.py
  - src/tests/fixtures/apps/realtime.py
  - src/tests/fixtures/asyncapi/realtime-3.0.0.json
  - src/tests/fixtures/asyncapi/realtime-3.1.0.json
  - docs/changelog.rst
  - docs/usage/websocket-handlers.rst
tests:
  - src/tests/integration/test_discovery.py
  - src/tests/unit/extractors/test_sse_routes.py
plan_revision: 3
plan_commit: 2fac422
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T21:10:00Z
last_verified_commit: 0371687
verification_evidence: "RED: ImportError for extract_sse_channels; integration tests found no SSE channels. GREEN: focused 25 passed. make lint 0, make type-check 0, make test 0 (254 passed, 96.63%; extractors/sse.py 100%), make validate-asyncapi 0 (realtime fixtures with SSE channels for 3.0.0 and 3.1.0). Litestar 2.24.0 exposes parsed_fn_signature, resolve_include_in_schema and http_methods identically."
created_at: 2026-11-04T20:40:00Z
updated_at: 2026-11-04T21:10:00Z
commit: 0371687
tags: [discovery, sse, http, tdd]
---

# Discover Server-Sent Event routes as send-only channels

## Objective

HTTP handlers returning `litestar.response.ServerSentEvent` appear as channels with one `send` operation, a `text/event-stream` message, an `http` channel binding and `x-litestar-source: sse`, typed by AsyncAPI decorators, behind `AsyncAPIConfig.include_sse_routes`.

## Context

- **Why `behavior_tdd`.** New discovery source with observable channels.
- **Invariants.** Master Decision 3: key `route.path_format`, suffixed `:sse` when a WebSocket route shares the path, `:sse:{method}` when several methods serve SSE; inclusion through `resolve_include_in_schema()`; only AsyncAPI decorator metadata is read (no HTTP `summary`/`description`/`operation_id`); a `receive` declaration raises; payload types stay Python types until `_build_message`.
- **Public API only.** `parsed_fn_signature`, `resolve_include_in_schema`, `http_methods` and `HTTPRoute.route_handler_map` are public Litestar API, so no `_compat.py` helper is needed.
- **Canonical tests.** `src/tests/integration/test_discovery.py` through `AsyncAPIGenerator.build_schema`; extractor edge cases in `src/tests/unit/extractors/test_sse_routes.py`.

## Steps

1. Write failing tests (RED) for every case in the spec deliverables.
2. Implement (GREEN) `asyncapi/extractors/sse.py::extract_sse_channels`, export it, call it from `generator.py::_discover_channels`, add `config.py::AsyncAPIConfig.include_sse_routes`.
3. Extend `tests.fixtures.apps.realtime` with SSE routes and re-export the fixtures.
4. Refactor and verify; changelog and usage notes.

## Verification

- **Initial:** `uv run pytest src/tests/integration/test_discovery.py src/tests/unit/extractors/test_sse_routes.py -q --no-cov` fails (no SSE channels / import error).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Undecorated SSE routes produce a send channel with an unconstrained `text/event-stream` message.
- [x] Decorated SSE routes carry the typed payload and path parameters; HTTP OpenAPI metadata is not copied; `receive` raises.
- [x] `include_in_schema=False` on a handler or router, a disabled flag, and non-SSE `Stream` routes produce nothing.
- [x] Shared WebSocket paths and multi-method SSE routes get the suffixed keys with the path as address.
- [x] The realtime fixture includes SSE channels and passes `make validate-asyncapi`.

## Notes & Discoveries

- [2026-11-04 20:50] No `_compat.py` helper was needed: handler detection uses public `parsed_fn_signature.return_type.is_subclass_of(ServerSentEvent)`, `resolve_include_in_schema()` and `http_methods`.
- [2026-11-04 20:55] The default operation key is the sanitized `{channel_key}_send`, for example `api_ticks_symbol__send`; this is the existing id sanitizer, not a new rule.
- [2026-11-04 21:00] A WebSocket route at the same path forces the `:sse` suffix whether or not that socket is documented, so SSE keys do not depend on another handler's visibility.
- [2026-11-04 21:05] `use_handler_docstrings` is not applied to SSE operations; only AsyncAPI decorator metadata is read.
