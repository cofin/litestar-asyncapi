---
type: Guide
title: "Architecture 03: Route Discovery & Extractors"
description: Native finalized routes, explicit contracts and truthful transport discovery.
tags: [architecture, extractors, discovery, websocket, channels]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: ws
    resource: src/litestar_asyncapi/asyncapi/extractors/websocket.py::extract_websocket_channels
    title: WebSocket discovery
  - id: ch
    resource: src/litestar_asyncapi/asyncapi/extractors/channels.py::extract_channels_plugin_channels
    title: ChannelsPlugin discovery
  - id: compat
    resource: src/litestar_asyncapi/_compat.py::websocket_signature
    title: Private Litestar handler access
---

# Route discovery

Extractors inspect finalized app routes[^ws] and return shared typed definitions with channel/operation provenance. Python payload types survive until assembly. Native private signatures, handler identity, DTO context and frame modes are isolated in _compat.py.[^compat]

Listener input is application receive; listener output and streams are application send. Nested native routes retain their prefixes and layered inclusion options. DTO-backed fields use Litestar's public create_openapi_schema hook rather than the unprojected model. Automatic DTO examples are omitted with a warning; explicit wire examples are supported.

Raw WebSocket handlers need explicit metadata by default. include_raw_websocket_routes=True permits unconstrained messages with an uncertainty warning; ordinary socket parameters never establish payload contracts.

# ChannelsPlugin

Only actual generated routes are discovered.[^ch] Internal subscription names create no endpoints when route creation is disabled. Generated fixed and parameterized native callbacks are identified by callback/owner identity and emit send-only operations; generic discovery excludes these callbacks to prevent duplication. User sockets sharing a prefix are retained. Explicit ChannelDefinition entries document broker transports or external endpoints.

# Wire modes

Logical payload content type is distinct from text/binary frame mode. The library's x-websocket-mode message extension records the native carrier, with explicit extensions taking precedence. Listener strings, bytes and structured JSON follow native serialization. Mixed/unknown streams do not imply JSON; the document default content type is None unless explicitly configured.

[^ws]: `src/litestar_asyncapi/asyncapi/extractors/websocket.py::extract_websocket_channels`
[^ch]: `src/litestar_asyncapi/asyncapi/extractors/channels.py::extract_channels_plugin_channels`
[^compat]: `src/litestar_asyncapi/_compat.py::websocket_signature`
