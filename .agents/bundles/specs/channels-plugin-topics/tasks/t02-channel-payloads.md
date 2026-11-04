---
type: Task
id: channels-plugin-topics:t02
title: Type ChannelsPlugin topic payloads through channel_payloads
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [t01]
files:
  - src/litestar_asyncapi/asyncapi/extractors/channels.py
  - src/litestar_asyncapi/config.py
  - src/tests/fixtures/apps/realtime.py
  - src/tests/fixtures/asyncapi/realtime-3.0.0.json
  - src/tests/fixtures/asyncapi/realtime-3.1.0.json
  - docs/changelog.rst
  - docs/usage/channels-plugin.rst
tests:
  - src/tests/integration/test_discovery.py
  - src/tests/unit/extractors/test_channels_plugin.py
plan_revision: 3
plan_commit: b99e4ee
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T22:20:00Z
last_verified_commit: 8327249
verification_evidence: "RED: TypeError, AsyncAPIConfig has no channel_payloads (5 tests). GREEN: focused file green. make lint 0, make type-check 0, make test 0 (264 passed, 96.68%), make validate-asyncapi 0. Installed wheel suite 264 passed on Litestar 2.24.0 and 2.25.0 (Python 3.12); make installed-test itself exits 2 in its minimal-install smoke step on both boundaries, a pre-existing failure (see notes)."
created_at: 2026-11-04T21:20:00Z
updated_at: 2026-11-04T22:20:00Z
commit: 8327249
tags: [discovery, channels-plugin, tdd]
---

# Type ChannelsPlugin topic payloads through channel_payloads

## Objective

`AsyncAPIConfig.channel_payloads` maps a topic name to a payload type. Fixed-topic generated routes and topic-only channels get the generated schema with `contentType: application/json`; generated routes keep `x-websocket-mode`; the arbitrary-channel route stays untyped.

## Context

- **Why `behavior_tdd`.** New configuration with observable message output.
- **Invariants.** Master Decision 5: keys are validated whatever the include flags say; an unknown key raises unless a plugin allows arbitrary channels, in which case it declares a topic that gets a topic-only channel. Payload types stay Python types until `generator.py::_build_message`, which owns schema generation through `AsyncAPISchemaGenerator`.
- **Canonical tests.** `src/tests/unit/extractors/test_channels_plugin.py` through `AsyncAPIGenerator.build_schema`.

## Steps

1. Write failing tests (RED): typed route and topic-only payloads; unknown key with every include flag; arbitrary mode with and without a key.
2. Implement (GREEN) `config.py::AsyncAPIConfig.channel_payloads` and key validation and message typing in `extractors/channels.py`.
3. Type a fixture topic and a fixture route; changelog and usage notes.

## Verification

- **Initial:** `uv run pytest src/tests/unit/extractors/test_channels_plugin.py -q --no-cov` fails (`channel_payloads` unknown).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`; `make installed-test LITESTAR_BOUNDARY=minimum` and `latest` exit `0`.

## Acceptance Criteria

- [x] Typed payloads on generated routes and topic-only channels with `application/json`; `x-websocket-mode` kept on routes.
- [x] Unknown keys raise regardless of include flags; arbitrary mode declares topics instead.
- [x] The arbitrary-channel route stays untyped.

## Notes & Discoveries

- [2026-11-04 22:00] Declared topics (unlisted keys under arbitrary mode) are appended to the first arbitrary-channel plugin's snapshot. They come from configuration, not runtime subscriptions, so they are emitted even when an arbitrary-mode plugin has no init snapshot.
- [2026-11-04 22:15] `make installed-test` fails in its minimal-install smoke step for both `LITESTAR_BOUNDARY=minimum` and `latest`: plain `litestar` without pydantic cannot import `litestar._openapi.schema_generation.examples`, which `_compat.py` has imported unchanged since the baseline. The target's full suite step was run by hand against the built wheel instead: 264 passed on 2.24.0 and on 2.25.0. Fixing the smoke step belongs to the release-ci domain.
- [2026-11-04 22:20] litestar-vite's classifier, imported read-only and run against `realtime-3.0.0.json` and `realtime-3.1.0.json`, maps every discovered channel to its `x-litestar-source` (websocket 2, sse 2, channels 3 per document, 0 mismatches); the explicit `audit` channel has no marker and falls to the classifier's `channels` default.
