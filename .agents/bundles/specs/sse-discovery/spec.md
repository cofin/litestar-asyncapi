---
type: Spec
flow_id: sse-discovery
title: Server-Sent Event Route Discovery
description: Discover HTTP routes returning ServerSentEvent as send-only channels with typed payloads from decorators.
state: draft
parent_prd: realtime-discovery
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [discovery, sse, http]
---

# Server-Sent Event Route Discovery

## Charter

Implement Master Decision 3: HTTP routes that return `litestar.response.ServerSentEvent` appear as send-only channels.

## Upstream Dependencies

- `channel-source-markers`, which adds `DiscoverySource.SSE` and the marker mapping.

## Key Deliverables

- `asyncapi/extractors/sse.py::extract_sse_channels(app, *, schema_generator, config)`, exported from `asyncapi/extractors/__init__.py`. `generator.py::_discover_channels` calls it when `AsyncAPIConfig.include_sse_routes` is true.
- Handler detection reads the resolved return annotation through Litestar's parsed signature. A small `_compat.py` helper is added only if a private attribute is needed.
- Inclusion uses `handler.resolve_include_in_schema()`, not the WebSocket `opt` check. Only AsyncAPI decorator metadata is read (`@asyncapi_operation`, `@asyncapi_message(action="send", ...)`). HTTP OpenAPI `summary`, `description` and `operation_id` are not copied. A `receive` action on an SSE handler raises `ImproperlyConfiguredException`.
- Channel output follows Master Decision 3, including the key-collision suffixes, with `bindings={"http": {}}` and `x-litestar-source: sse`.
- `AsyncAPIConfig.include_sse_routes: bool = True`, with an inline field docstring.
- Tests:
  - an SSE route without decorators;
  - an SSE route with a typed payload and path parameters;
  - `include_in_schema=False` on the handler and on its router;
  - an SSE GET and a WebSocket route on the same path;
  - GET and POST SSE handlers on one path;
  - an SSE route on a nested router;
  - the flag turned off;
  - a non-SSE `Stream` route, which is ignored.
- The generated validation fixture includes an SSE channel.

## Public Seams

- `litestar_asyncapi.asyncapi.extractors.extract_sse_channels`
- `AsyncAPIConfig.include_sse_routes`
- `asyncapi_message` and `asyncapi_operation` on HTTP handlers

## Acceptance Boundary

The tests pass, and `make validate-asyncapi` passes with the SSE fixture.
