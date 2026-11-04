---
type: Task
id: channel-source-markers:t01
title: Mark discovered channels with their transport and bindings
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/litestar_asyncapi/asyncapi/datastructures.py
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/asyncapi/extractors/websocket.py
  - src/litestar_asyncapi/asyncapi/extractors/channels.py
  - src/tests/fixtures/apps/realtime.py
  - src/tests/fixtures/asyncapi/realtime-3.0.0.json
  - src/tests/fixtures/asyncapi/realtime-3.1.0.json
  - Makefile
  - docs/changelog.rst
  - docs/usage/websocket-handlers.rst
  - docs/usage/channels-plugin.rst
tests:
  - src/tests/integration/test_discovery.py
  - src/tests/integration/test_cli.py
plan_revision: 3
plan_commit: 5e875e6
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T20:30:00Z
last_verified_commit: 05d8ec8
verification_evidence: "RED: test_discovered_channels_carry_transport_markers failed with TypeError (ChannelDefinition has no description). GREEN: focused file 20 passed. make lint 0, make type-check 0, make test 0 (249 passed, 96.54%), make validate-asyncapi 0 (realtime-3.0.0/3.1.0 validated)"
created_at: 2026-11-04T20:00:00Z
updated_at: 2026-11-04T20:30:00Z
commit: 05d8ec8
tags: [discovery, bindings, extensions, tdd]
---

# Mark discovered channels with their transport and bindings

## Objective

Every discovered channel carries `x-litestar-source` (`websocket` or `channels`) and an explicit `bindings` object: `ws` on native WebSocket channels and `{}` on ChannelsPlugin channels. Explicit config channels carry their own `description` and `extensions` and no automatic marker.

## Context

- **Why `behavior_tdd`.** New observable wire output on `channels.<key>`.
- **Invariants.** Explicit `ChannelDefinition` fields copy through `_discover_channels` by field name; the marker is applied once in `generator.py::_populate_channels` from a single `DiscoverySource` mapping in `datastructures.py`; explicit extensions win over the inferred marker; extension keys start with `x-`.
- **Canonical tests.** `src/tests/integration/test_discovery.py` through `AsyncAPIGenerator.build_schema`; a generated `realtime-*` fixture under `src/tests/fixtures/asyncapi/` kept in sync by `test_cli.py` and validated by `make validate-asyncapi`.

## Steps

1. Write failing tests (RED) in `test_discovery.py` for a native listener, a ChannelsPlugin route under `/ws/`, and an explicit channel with `description` and `extensions`.
2. Implement (GREEN): `DiscoverySource.SSE` and the marker mapping in `asyncapi/datastructures.py`; `ChannelDefinition.description`/`extensions`; `generator.py::_populate_channels`; bindings in `extractors/websocket.py::extract_websocket_channels` and `extractors/channels.py::extract_channels_plugin_channels`.
3. Add `tests.fixtures.apps.realtime` with 3.0.0 and 3.1.0 apps, export it from `export-asyncapi-fixture`, and add the drift check.
4. Refactor and verify; changelog and usage notes.

## Verification

- **Initial:** `uv run pytest src/tests/integration/test_discovery.py -q --no-cov` fails on missing `bindings` / `x-litestar-source`.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Native listener channels carry `x-litestar-source: websocket` and `bindings: {ws: {}}`.
- [x] ChannelsPlugin channels under `/ws/` carry `x-litestar-source: channels` and `bindings: {}`.
- [x] Explicit channels keep their own `description` and `extensions` and get no marker.
- [x] The generated realtime fixture passes `make validate-asyncapi` for 3.0.0 and 3.1.0.

## Notes & Discoveries

- [2026-11-04 20:10] The marker is applied once in `_populate_channels` from `SOURCE_MARKERS`, so extractors only set bindings; explicit `extensions` on a discovered channel would win over the inferred marker.
- [2026-11-04 20:15] `DiscoverySource.CHANNELS_PLUGIN` keeps its `channels-plugin` value; the wire marker `channels` comes from the mapping, not the enum value.
- [2026-11-04 20:20] The generated fixture lives in `tests.fixtures.apps.realtime`; the `bindings` drift test is parametrized over both generated fixture families.
