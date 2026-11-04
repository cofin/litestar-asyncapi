---
type: Spec
flow_id: realtime-discovery
title: Realtime Source Discovery for Downstream Codegen
description: Mark each discovered channel's transport, discover Server-Sent Event routes, and discover typed ChannelsPlugin topics, so client code generators such as litestar-vite need no heuristics or duplicated contracts (issue #11).
state: completed
parent_prd: null
research: []
plan_revision: 3
plan_commit: 5e875e6
state_revision: 0
current_task: null
last_verified_checkpoint: 8327249
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T22:20:00Z
tags: [prd, discovery, sse, channels-plugin, bindings, codegen]
---

# Realtime Source Discovery for Downstream Codegen

## 1. North Star Goal & Context

### Objectives

An application's realtime endpoints all appear in its AsyncAPI document with typed payloads and a clear transport marker. This covers WebSocket handlers, Server-Sent Event streams and ChannelsPlugin topics. A client generator can then emit the right client for each channel by reading the document alone.

### Current State & Limits

Issue #11, filed after litestar-vite removed its own AsyncAPI fallback generator, names three gaps:

- **SSE routes are invisible.**
  - `asyncapi/generator.py::_discover_channels` runs only `extract_websocket_channels` and `extract_channels_plugin_channels`, and both accept only `WebSocketRoute`.
  - `litestar.response.ServerSentEvent` is not generic (it subclasses `Stream`), so a payload type can only come from decorators.
- **ChannelsPlugin topics are thin.**
  - `extractors/channels.py::extract_channels_plugin_channels` sees only generated WebSocket routes. Litestar's default is `ChannelsPlugin(create_ws_route_handlers=False)`, so most configured topics are never discovered.
  - Every message gets an untyped `Schema()` payload.
- **There is no transport marker.** No discovered channel carries `bindings`, so litestar-vite falls back to guessing.
  - Its classifier (`litestar_vite/codegen/_asyncapi.py`) reads a `ws` binding as "websocket", an `http` binding as "sse", and any other bindings object as "channels".
  - When `bindings` is absent, `_derive_channel_bindings` guesses `ws` from a `/ws` address prefix or a `receive` operation. That misclassifies ChannelsPlugin channels under `/ws/`.
  - ChannelsPlugin routes are WebSocket routes too, so a `ws` binding alone cannot tell them apart from native handlers.

### What Is New & Why It Succeeds

- Every discovered channel carries `x-litestar-source`, set to `websocket`, `channels` or `sse`. These are exactly the values litestar-vite already uses, so its classifier can read the field directly instead of guessing.
- Every discovered channel carries an explicit `bindings` object, which is what litestar-vite's classifier expects:
  - native WebSocket channels get `ws`;
  - SSE channels get `http`;
  - ChannelsPlugin channels get an empty `{}`.

  An explicit object, even an empty one, means litestar-vite never falls back to guessing.
- A new SSE extractor and topic-level ChannelsPlugin discovery fill the two missing sources. `AsyncAPIConfig.channel_payloads` maps a topic name to a payload type without the full `ChannelDefinition` boilerplate.

### Impact

- **litestar-vite** gets back what its removed fallback generator used to provide: SSE channels, typed topics and deterministic transport mapping.
- **Every docs-UI user** sees SSE streams and Channels topics that are missing from the docs today.

### Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Topic-only channels have no client-connectable route, which may confuse docs readers. | A channel description says they are broker topics, and `include_channels_plugin_topics=False` hides them. |
| Reading ChannelsPlugin topics needs private attributes (`_channels`, `_handler_root_path`). | `_compat.py` only, tested in both `LITESTAR_BOUNDARY=minimum` and `latest` lanes. The files are byte-identical in Litestar 2.24.0 and 2.25.0. |
| `ChannelsPlugin.subscribe` adds runtime topics to `_channels` when arbitrary channels are allowed. | Topics are snapshotted once in `AsyncAPIPlugin.on_app_init`, from the configured list, before any subscription. |
| Newly discovered channels change existing documents. | This is a pre-1.0 additive change, recorded in the changelog. Each new source has its own off switch. |
| `http` binding semantics: the official channel-level `http` binding is a reserved empty object. | Emit only `{"http": {}}` at the channel level. Validate it through `make validate-asyncapi`. |

### Success Metrics

- A fixture app with a native listener, an SSE route and a ChannelsPlugin with both route-backed and topic-only channels exports a document that:
  - passes `make validate-asyncapi` for 3.0.0 and 3.1.0;
  - shows each channel's `x-litestar-source`;
  - shows typed payloads where declared.
- litestar-vite's current classifier maps every channel of that document correctly with no code change. This is verified by running its classifier against the exported fixture once, recorded in task notes.

## 2. Locked Architectural Decisions

1. **Transport marker.** Each discovered channel gets a channel extension, `x-litestar-source`, mapped from `DiscoverySource`:
   - `WEBSOCKET` → `websocket`
   - `CHANNELS_PLUGIN` → `channels`
   - a new `SSE` → `sse`

   `ChannelDefinition` gains `description` and `extensions`, copied by `generator.py::_populate_channels`, so explicit channels can carry their own marker. Explicit channels get no automatic marker.
   - Rejected: bindings only, because ChannelsPlugin and native WebSocket routes would be indistinguishable.
2. **Every discovered channel gets an explicit bindings object.**
   - `WebSocketChannelBinding()` on native WebSocket channels.
   - `{"http": {}}` on SSE channels.
   - An empty `{}` on ChannelsPlugin channels, both route-backed and topic-only.

   `BaseSchemaObject.to_schema` keeps an empty dict, and the official schema accepts it. An empty object stops litestar-vite's derivation from guessing `ws` for `/ws/` addresses.
   - Rejected: omitting bindings on ChannelsPlugin channels. litestar-vite would derive `ws` for them.
   - Rejected: a `ws` binding on ChannelsPlugin channels. litestar-vite would read them as native sockets.
3. **SSE discovery.**
   - **Extractor.** `asyncapi/extractors/sse.py::extract_sse_channels(app, *, schema_generator, config)`, exported from `asyncapi/extractors/__init__.py`, behind `AsyncAPIConfig.include_sse_routes: bool = True`.
   - **Which handlers.** An `HTTPRouteHandler` qualifies when its resolved return annotation is `ServerSentEvent` and `handler.resolve_include_in_schema()` is true, which honors router and controller layers.
   - **Key.** `route.path_format`. If that key is taken by another source (a WebSocket route at the same path), or the route has several SSE methods, the key becomes `{path_format}:sse` or `{path_format}:sse:{method}`. The address stays the path.
   - **Metadata.** Only AsyncAPI decorator metadata is read. HTTP OpenAPI fields (`summary`, `description`, `operation_id`) are not copied, because they describe the HTTP operation.
   - **Channel.** `key` and `address` are `route.path_format`, and the parameters come from `_path_parameters_to_parameters`.
   - **Operation.** One `send` operation.
   - **Message.** The payload comes from `@asyncapi_message(action="send", payload=...)`, or `{}` without one. `contentType` is always `text/event-stream`.
4. **ChannelsPlugin topics.** Accessed through a new `_compat.py::channels_plugin_topics(plugin)`, which returns the configured topic names and the handler root path.
   - **Snapshot.** Topics come only from the names passed to the `ChannelsPlugin` constructor, snapshotted in `on_app_init`. Runtime subscriptions never change the document.
   - **Flag.** `AsyncAPIConfig.include_channels_plugin_topics: bool = True` applies only when `include_channels_plugin` is true.
   - **Topic-only channels.** Every configured topic without a generated WebSocket route becomes a channel with `key` and `address` equal to the topic name, the description "ChannelsPlugin broker topic", and one `send` operation with the id `{topic}_send`, sanitized like other ids.
   - **Route mapping.** A generated fixed-topic route maps to `path_format.removeprefix(handler_root_path)`. The arbitrary-channel route is recognized through `generated_channels_mode`.
   - **Collisions.** A topic key that equals another channel key (a path, or an explicit config key) raises `ImproperlyConfiguredException`, naming both sources. Several ChannelsPlugins with the same topic also raise.
   - `arbitrary_channels_allowed` without configured names adds nothing.
5. **Typed topic payloads.** `AsyncAPIConfig.channel_payloads: Mapping[str, Any]` (user choice) maps a topic name to a payload type.
   - It applies to fixed-topic generated routes and to topic-only channels. Messages get the generated schema with `contentType: application/json`. Generated routes keep `x-websocket-mode`.
   - **Key validation.** Keys are always validated, whatever the include flags say. A key that names no configured topic raises `ImproperlyConfiguredException` at build time. When `arbitrary_channels_allowed=True`, an unlisted key instead declares a topic, which then gets a topic-only channel.
   - The arbitrary-channel route (`.../{channel_name}`) keeps its untyped payload.
   - Rejected: a `ChannelDefinition.for_topic` helper, which is more verbose and duplicates `AsyncAPIConfig.channels`.
6. **Sequencing.** This PRD lands after `contract-fixes` chapters `public-hygiene` and `discovery-fixes` (user decision). It builds on the split listener helpers and the simplified `_path_parameters_to_parameters`.

## 3. Master Roadmap (Ordered Child Flows)

| Chapter | Flow ID | Title | Key Deliverables | Public Seams | Dependencies | State |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `channel-source-markers` | Transport markers | `x-litestar-source` on discovered channels, `ws` binding on native WebSocket channels | Generated `channels` objects | `discovery-fixes` | completed |
| 2 | `sse-discovery` | Server-Sent Event routes | `extract_sse_channels`, `include_sse_routes`, decorator support on HTTP handlers, `http` binding | `asyncapi.extractors.extract_sse_channels`, `AsyncAPIConfig.include_sse_routes` | 1 | completed |
| 3 | `channels-plugin-topics` | Typed ChannelsPlugin topics | Topic-only discovery, `include_channels_plugin_topics`, `channel_payloads` | `AsyncAPIConfig.channel_payloads`, `AsyncAPIConfig.include_channels_plugin_topics` | 1 | completed |

Chapters 2 and 3 are independent after chapter 1. Both add fields to `config.py`, so land 2 then 3.

## 4. Global Constraints (Applicable to All Child Flows)

- Load `asyncapi-generation` before changing code, and `review-asyncapi-generation` for review. Chapter 3's schema attachment also loads `asyncapi-schema`.
- Write tests first at public seams: `AsyncAPIGenerator.build_schema` and `AsyncAPIPlugin.get_asyncapi_schema`, in `src/tests/integration/test_discovery.py` and `src/tests/unit/extractors/`.
- Every new document shape is covered by a generated fixture in `make validate-asyncapi` for 3.0.0 and 3.1.0.
- Private Litestar access only in `_compat.py`. New `AsyncAPIConfig` fields get inline field docstrings, per `docs-redesign`.
- Usage docs for each new source go into whichever usage pages exist at merge time.
- Public text (commits, PR, changelog, the issue reply) carries no planning labels or internal names.

## 5. Backlog (Deferred Items)

- litestar-vite reads `x-litestar-source` before its binding heuristic. That change lives in the litestar-vite repository.
- `ws` channel binding `query`/`headers` schemas derived from route parameters (also in the `contract-fixes` backlog).
- Inferring SSE payloads from generator yield types. `ServerSentEvent` takes the generator at runtime, so the return annotation carries no item type.
- Per-topic payloads on the arbitrary-channel route (for example a `oneOf` over `channel_payloads`).

## Implementation Plan

- [x] [05d8ec8] channel-source-markers — transport markers and ws bindings on discovered channels (../channel-source-markers/spec.md)
- [x] [0371687] sse-discovery — Server-Sent Event route discovery (../sse-discovery/spec.md)
- [x] [8327249] channels-plugin-topics — topic-only discovery and typed topic payloads (../channels-plugin-topics/spec.md)

## Continuity Snapshot

- **State:** completed. Chapter 1 at `05d8ec8`, chapter 2 at `0371687`, chapter 3 at `d3def2e`, `bc99dcf` and `8327249`.
- **Success metric:** litestar-vite's unchanged classifier maps every discovered channel of the generated realtime fixture (3.0.0 and 3.1.0) to its `x-litestar-source`, with 0 mismatches.
- **Decisions on 2026-11-04 (user):** `channel_payloads` mapping; topic-only discovery on by default; sequenced after `discovery-fixes`.
- **Review:** round 1 of the independent review is adjudicated. All 9 findings were adopted, and `plan_revision` is now 2.
- **Discoveries:** litestar-vite guesses `ws` when bindings are absent, so ChannelsPlugin channels need an explicit empty object.
