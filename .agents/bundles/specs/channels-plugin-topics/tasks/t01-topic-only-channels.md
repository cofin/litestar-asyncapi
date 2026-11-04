---
type: Task
id: channels-plugin-topics:t01
title: Discover configured ChannelsPlugin topics as topic-only channels
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/litestar_asyncapi/_compat.py
  - src/litestar_asyncapi/plugins/core.py
  - src/litestar_asyncapi/asyncapi/extractors/channels.py
  - src/litestar_asyncapi/asyncapi/generator.py
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
last_verified_at: 2026-11-04T21:50:00Z
last_verified_commit: d3def2e
verification_evidence: "RED: topic channels absent, collisions did not raise, arbitrary-route test lacked the news topic. GREEN: focused file green. make lint 0, make type-check 0, make test 0 (257 passed, 96.65%), make validate-asyncapi 0 (realtime fixtures with route-backed and topic-only ChannelsPlugin channels)"
created_at: 2026-11-04T21:20:00Z
updated_at: 2026-11-04T21:50:00Z
commit: d3def2e
tags: [discovery, channels-plugin, tdd]
---

# Discover configured ChannelsPlugin topics as topic-only channels

## Objective

Every topic passed to a `ChannelsPlugin` constructor that has no generated fixed-topic WebSocket route becomes a channel keyed by the topic name, with the description "ChannelsPlugin broker topic", empty bindings, `x-litestar-source: channels` and one `send` operation `{topic}_send`, behind `AsyncAPIConfig.include_channels_plugin_topics`.

## Context

- **Why `behavior_tdd`.** New channels in the generated document.
- **Invariants.** Master Decision 4: topics come from `_compat.py::channels_plugin_topics`, snapshotted in `AsyncAPIPlugin.on_app_init` so runtime subscriptions never leak; generated fixed-topic routes map to `path_format.removeprefix(root_path)`; the arbitrary-channel route covers no specific topic; a topic key equal to another channel key or configured on two plugins raises naming both sources. Private Litestar attributes are read only in `_compat.py`.
- **Canonical tests.** `src/tests/unit/extractors/test_channels_plugin.py` and `src/tests/integration/test_discovery.py` through `AsyncAPIGenerator.build_schema` and `AsyncAPIPlugin.get_asyncapi_schema`.

## Steps

1. Write failing tests (RED): two topics without routes; routes without duplicates; runtime subscription absent; path and config key collisions; shared topic across plugins; flag off.
2. Implement (GREEN) `_compat.py::channels_plugin_topics` and `generated_channels_plugin`, the snapshot in `plugins/core.py::AsyncAPIPlugin.on_app_init`, topic-only channels in `extractors/channels.py::extract_channels_plugin_channels`, the config-key collision in `generator.py::_discover_channels`, and `config.py::AsyncAPIConfig.include_channels_plugin_topics`.
3. Extend the realtime fixture with topic-only channels; changelog and usage notes.

## Verification

- **Initial:** `uv run pytest src/tests/unit/extractors/test_channels_plugin.py src/tests/integration/test_discovery.py -q --no-cov` fails (no topic channels).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Topics without generated routes become topic-only channels; route-backed topics are not duplicated.
- [x] Runtime subscriptions never appear in the document.
- [x] Collisions with a path, a config key or another plugin raise naming both sources.
- [x] `include_channels_plugin_topics=False` hides topic-only channels.

## Notes & Discoveries

- [2026-11-04 21:30] (Superseded by the 22:05 note for snapshot-less builds.) The arbitrary-channel route (`{channel_name}`) covers no specific topic, so configured topics on an arbitrary plugin with generated routes still get topic-only channels; `test_actual_channels_routes_are_deduplicated_by_native_identity[True]` now expects `news`.
- [2026-11-04 21:35] Provenance strings use the plugin's position among the app's ChannelsPlugin instances: `ChannelsPlugin[0] topic 'news'`. Topic/path collisions reuse the `_normalize_channels` raise; topic/config collisions raise in `_discover_channels` before explicit channels replace discovered ones.
- [2026-11-04 21:40] Ruff forbids lazy imports and private access in `generator.py`, so the snapshot lookup lives in `extractors/channels.py::_configured_topics`, which reads `AsyncAPIPlugin._channels_topics` and falls back to a live read when the app has no AsyncAPIPlugin (direct `AsyncAPIGenerator` use). `extract_channels_plugin_channels` gained only `config`.
- [2026-11-04 21:45] `_compat.generated_channels_mode` now delegates to the new `generated_channels_plugin`, which returns the owning plugin.
- [2026-11-04 22:05] Review follow-up `bc99dcf` (`fix: never publish runtime-subscribed channel topics`): the snapshot-less fallback read ChannelsPlugin's live `_channels`, which `subscribe` grows in arbitrary mode, so client-chosen topic names could reach the document (reproduced: `runtime` appeared). `_compat.channels_plugin_topics(plugin, at_init=...)` now returns an arbitrary-mode plugin's names only at init; without the AsyncAPIPlugin snapshot such a plugin contributes no topic channels. Regression tests cover runtime subscriptions with and without the snapshot and a standalone arbitrary-mode build. make lint/type-check/test (259 passed, 96.65%)/validate-asyncapi exit 0.
