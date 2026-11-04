---
type: Spec
flow_id: channels-plugin-topics
title: Typed ChannelsPlugin Topics
description: Discover configured ChannelsPlugin topics without generated routes and attach payload types through AsyncAPIConfig.channel_payloads.
state: completed
parent_prd: realtime-discovery
research: []
plan_revision: 3
plan_commit: b99e4ee
state_revision: 0
current_task: null
last_verified_checkpoint: 8327249
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T22:20:00Z
tags: [discovery, channels-plugin, schema]
---

# Typed ChannelsPlugin Topics

## Charter

Implement Master Decisions 4 and 5. Configured ChannelsPlugin topics appear even under Litestar's default `create_ws_route_handlers=False`, and users can type a topic's payload with one mapping entry.

## Upstream Dependencies

- `channel-source-markers`.

## Key Deliverables

- `_compat.py::channels_plugin_topics(plugin)` returns the configured topic names, the handler root path and whether arbitrary channels are allowed. `AsyncAPIPlugin.on_app_init` calls it once, so runtime subscriptions never leak into the document.
- `extractors/channels.py` work:
  - Topic-only channels, route-to-topic mapping and collision errors follow Master Decision 4. All ChannelsPlugin channels carry `bindings={}`.
- `AsyncAPIConfig.include_channels_plugin_topics: bool = True` (applies only when `include_channels_plugin` is true) and `AsyncAPIConfig.channel_payloads: Mapping[str, Any]` (default empty), both with inline field docstrings.
- A `channel_payloads` entry replaces that topic's untyped message with a generated schema and `contentType: application/json`. Generated routes keep `x-websocket-mode`. Key validation follows Master Decision 5, including arbitrary mode. The arbitrary-channel route stays untyped.
- Tests:
  - `create_ws_route_handlers=False` with two topics;
  - `create_ws_route_handlers=True`, where nothing is duplicated;
  - a typed payload on each kind of channel;
  - an unknown key;
  - `arbitrary_channels_allowed` only, and with a `channel_payloads` key;
  - a topic subscribed at runtime, which stays absent;
  - a topic key colliding with a path or config key;
  - two ChannelsPlugins sharing a topic;
  - the flag turned off.

## Public Seams

- `AsyncAPIConfig.channel_payloads`
- `AsyncAPIConfig.include_channels_plugin_topics`
- The generated `channels` objects

## Acceptance Boundary

The tests pass, `make validate-asyncapi` passes with the topic fixture, and `make installed-test` passes with `LITESTAR_BOUNDARY=minimum` and `LITESTAR_BOUNDARY=latest`.

## Implementation Plan

- [x] [d3def2e] t01 — discover configured topics as topic-only channels from an init-time snapshot (tasks/t01-topic-only-channels.md); review fix [bc99dcf]
- [x] [8327249] t02 — type topic payloads through `AsyncAPIConfig.channel_payloads` (tasks/t02-channel-payloads.md)

**Recovery checkpoint:** `make lint && make type-check && make test && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **State:** completed at `8327249`. `make lint`, `make type-check`, `make test` (264 passed, 96.68%) and `make validate-asyncapi` exit `0`. The installed-wheel suite passes on Litestar 2.24.0 and 2.25.0; `make installed-test` still fails in its pre-existing minimal-install smoke step.
- **Discoveries:** runtime subscriptions share the topic mapping in arbitrary mode, so topic names are read only at init (`bc99dcf`); the snapshot lookup lives in the extractor because `generator.py` may not use lazy imports or private access.
