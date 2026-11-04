---
type: Guide
title: Route and Topic Discovery
description: Finalized WebSocket and SSE routes, configured topics and transport provenance.
tags: [asyncapi, contracts]
status: stable
generated:
  by: flow-completion
  at: 2026-11-04
verified:
  - by: flow-completion
    at: 2026-11-04
    commit: dcc21c01b0e1e0bad5f4547dad61f075364629c2
sources:
  - id: ws
    resource: src/litestar_asyncapi/asyncapi/extractors/websocket.py::extract_websocket_channels
    title: WebSocket discovery
  - id: sse
    resource: src/litestar_asyncapi/asyncapi/extractors/sse.py::extract_sse_channels
    title: SSE discovery
  - id: ch
    resource: src/litestar_asyncapi/asyncapi/extractors/channels.py::extract_channels_plugin_channels
    title: Topic discovery
  - id: compat
    resource: src/litestar_asyncapi/_compat.py::generated_channels_topic
    title: Native fixed-topic identity
  - id: markers
    resource: src/litestar_asyncapi/asyncapi/datastructures.py::SOURCE_MARKERS
    title: Transport markers
---

# Route and Topic Discovery

<!-- truth: start -->
- Extractors consume finalized native routes and keep Python payload types until assembly.
- Listener input is application receive; listener output, streams, SSE and ChannelsPlugin publications are send.
- Configured topics can exist without routes; runtime subscriptions never become documented topics.
- Fixed generated ChannelsPlugin callbacks retain topic identity independently of normalized route paths.
- Discovered channels carry x-litestar-source: websocket, channels or sse; explicit extensions win.
<!-- truth: end -->

## WebSocket routes

The WebSocket extractor honors layered include_in_schema and excludes native ChannelsPlugin callbacks.[^ws] Listener operation names use the user callback name and action. Decorator overrides precede handler metadata and optional docstring fallbacks. Native DTOs supply wire schemas through their public hook; automatic DTO examples are omitted with a warning. Raw sockets require explicit contracts unless include_raw_websocket_routes enables warned placeholders.

## ChannelsPlugin topics

The plugin snapshots configured topic names during application initialization; arbitrary runtime subscriptions share native mutable state and must never enter documents.[^ch] Without a snapshot, arbitrary-mode discovery omits implicit topics. channel_payloads validates configured names, or declares names when arbitrary channels are allowed. Its keys remain validated when include flags disable discovery.

Fixed generated routes use callback closure identity to recover the original topic, including slashes in topic names and relative route roots.[^compat] Never reconstruct a topic by stripping a raw prefix from a normalized URL. Generated sockets are send-only, typed topics use application/json, and untyped sockets retain native frame content types. Configured topics without a matching generated route become broker channels, controlled by include_channels_plugin_topics. Explicit broker contracts require disabling automatic topic discovery to avoid conflicting keys.

## Server-Sent Events

Resolved ServerSentEvent return annotations identify HTTP SSE routes, including subclasses. Optional annotations containing None are not treated as streaming-only responses.[^sse] HTTP routes honor layered visibility, keep path parameters, and produce send-only messages with text/event-stream and an unconstrained payload unless decorator metadata supplies a type. Multiple visible methods receive deterministic suffixes. include_sse_routes disables this discovery independently.

## Transport identity

SOURCE_MARKERS centrally maps DiscoverySource to x-litestar-source.[^markers] WebSockets use a ws channel binding; SSE uses the reserved empty http binding; broker topics keep explicit empty bindings. Native x-websocket-mode records text/binary carriage separately from logical message content type. Explicit extensions win over inferred values.

[^ws]: `src/litestar_asyncapi/asyncapi/extractors/websocket.py::extract_websocket_channels`
[^sse]: `src/litestar_asyncapi/asyncapi/extractors/sse.py::extract_sse_channels`
[^ch]: `src/litestar_asyncapi/asyncapi/extractors/channels.py::extract_channels_plugin_channels`
[^compat]: `src/litestar_asyncapi/_compat.py::generated_channels_topic`
[^markers]: `src/litestar_asyncapi/asyncapi/datastructures.py::SOURCE_MARKERS`
