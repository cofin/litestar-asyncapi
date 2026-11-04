---
type: Glossary
title: AsyncAPI Contract Domain Glossary
description: One name per concept for channels, operations, messages, discovery provenance and wire documents across code, tests and specs.
tags: [domains, glossary, asyncapi, channels, operations]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: ds
    resource: src/litestar_asyncapi/asyncapi/datastructures.py::DiscoverySource
    title: Typed contracts and provenance
  - id: cfg
    resource: src/litestar_asyncapi/config.py::AsyncAPIConfig
    title: Document configuration
  - id: dec
    resource: src/litestar_asyncapi/decorators.py::asyncapi_operation
    title: Handler overrides
  - id: core
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin
    title: Canonical document cache
  - id: action
    resource: src/litestar_asyncapi/spec/enums.py
    title: Operation actions
---

# AsyncAPI Contract Domain Glossary

<!-- truth: start -->
- **Channel key** is the document identity under `channels`; **address** is the transport path. They differ: distinct keys may share an address.
- **Operation key** is the identity under `operations`; there is no wire `operationId`.
- **Action** is from the application's point of view: listener input is `receive`, listener output and streams are `send`.
- **Definition** (`ChannelDefinition`, `OperationDefinition`, `MessageDefinition`) is a typed contract shared by decorators and `AsyncAPIConfig.channels`.
- **Discovered** (`DiscoveredChannel`, `DiscoveredOperation`) adds provenance (`DiscoverySource`) only.
- **Canonical document** is the per-app cached `AsyncAPI` model plus its normalized dict and JSON bytes.
- `None` means "no override"; an explicit empty list means "override with nothing".
<!-- truth: end -->

## Terms

| Term | Meaning | Code |
| --- | --- | --- |
| Channel key | Stable document identity of a channel; an explicit key replaces matching inference | `ChannelDefinition`[^ds] |
| Address | Transport path, possibly parameterized (`/ws/{room}`) | `Channel.address` |
| Parameter | AsyncAPI 3 parameter: description/enum/default/examples/location only, no schema | `spec/channel.py::Parameter` |
| Operation key | Casefold-unique key in `operations`; suffixed `_2…` unless `strict_uniqueness` | `generator.py::_ensure_unique_operation_id` |
| Action | `send` or `receive`, from the application's perspective | `OperationAction`[^action] |
| Message choice | One of several named messages an operation may carry | `MessageDefinition` |
| Explicit contract | A `ChannelDefinition` in `AsyncAPIConfig.channels`, for brokers or external endpoints[^cfg] | `AsyncAPIConfig.channels` |
| Override | Decorator metadata layered onto an inferred handler[^dec] | `asyncapi_operation`, `asyncapi_message` |
| Provenance | Which source produced a discovered contract | `DiscoverySource` |
| Wire mode | Text vs binary frame carrier, recorded as `x-websocket-mode`; distinct from logical content type | extractors |
| Canonical document | Cached model, normalized dict and immutable JSON bytes for the one bound app[^core] | `AsyncAPIPlugin._get_document` |
| Trait | Reusable operation/message fragment from config | `AsyncAPIConfig.to_operation_traits` |

## Lifecycle

1. **Declare**: handlers, decorators and `AsyncAPIConfig.channels` express contracts with Python payload types.
2. **Discover**: extractors walk finalized routes and the `ChannelsPlugin`, producing `Discovered*` values with provenance.
3. **Merge**: explicit keys replace inference; compatible inferred contracts merge only for the same route identity; conflicts name both sources.
4. **Assemble**: payload types become schemas, examples become `MessageExample`, keys are deduplicated and `$ref` pointers escaped.
5. **Finalize**: schema component names are finalized, references validated, then the document is normalized with application encoders and cached.

## Boundaries

- Security declarations describe contracts; they never install runtime authorization.
- There is no automatic broker or SSE inference. Raw WebSocket handlers need explicit metadata unless `include_raw_websocket_routes=True`.

[^ds]: `src/litestar_asyncapi/asyncapi/datastructures.py::DiscoverySource`
[^cfg]: `src/litestar_asyncapi/config.py::AsyncAPIConfig`
[^dec]: `src/litestar_asyncapi/decorators.py::asyncapi_operation`
[^core]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin`
[^action]: `src/litestar_asyncapi/spec/enums.py`
