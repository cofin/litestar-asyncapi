---
type: Spec
flow_id: channel-source-markers
title: Transport Markers on Discovered Channels
description: Emit x-litestar-source on every discovered channel and a ws binding on native WebSocket channels.
state: completed
parent_prd: realtime-discovery
research: []
plan_revision: 3
plan_commit: 5e875e6
state_revision: 0
current_task: null
last_verified_checkpoint: 05d8ec8
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T20:30:00Z
tags: [discovery, bindings, extensions]
---

# Transport Markers on Discovered Channels

## Charter

Implement Master Decisions 1 and 2. Every channel produced by discovery says which transport it uses, and native WebSocket channels carry the standard `ws` channel binding.

## Upstream Dependencies

- `discovery-fixes`, from the `contract-fixes` PRD.

## Key Deliverables

- `DiscoverySource` gains `SSE = "sse"`. A single mapping from `DiscoverySource` to the extension value lives next to the enum in `asyncapi/datastructures.py`.
- `ChannelDefinition` and `DiscoveredChannel` gain `description` and `extensions`, and `generator.py::_populate_channels` copies both. Discovered channels get `extensions["x-litestar-source"]`.
- `extractors/websocket.py` sets `bindings={"ws": WebSocketChannelBinding()}`. `extractors/channels.py` sets `bindings={}`.
- Tests in `src/tests/integration/test_discovery.py` cover:
  - a native listener → `websocket` with a `ws` binding;
  - a ChannelsPlugin route under `ws_handler_base_path="/ws/"` → `channels` with `bindings: {}`;
  - an explicit config channel → no marker, while its own `description` and `extensions` are kept.
- The generated validation fixture is updated, and `make validate-asyncapi` passes.

## Public Seams

The generated `channels.<key>.bindings` and `channels.<key>.x-litestar-source`.

## Acceptance Boundary

The tests pass. The litestar-vite classifier check from the Master success metrics maps the fixture's WebSocket and ChannelsPlugin channels correctly.

## Implementation Plan

- [x] [05d8ec8] t01 — transport markers and bindings on discovered channels (tasks/t01-transport-markers.md)

**Recovery checkpoint:** `make lint && make type-check && make test && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **State:** completed at `05d8ec8`. `make lint`, `make type-check`, `make test` (249 passed, 96.54%) and `make validate-asyncapi` exit `0`.
- **Discoveries:** the marker is applied centrally in `_populate_channels`; the realtime fixture is the shared generated fixture for the remaining chapters.
