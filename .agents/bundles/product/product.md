---
type: Guide
title: Library Overview
description: Verified AsyncAPI generation, documentation and interaction boundaries for litestar-asyncapi.
tags: [product, overview, asyncapi, litestar]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: pkg
    resource: pyproject.toml::project
    title: Package metadata and Litestar dependency
  - id: api
    resource: src/litestar_asyncapi/__init__.py
    title: Public API surface
  - id: pkgjson
    resource: package.json
    title: Pinned UI and validator versions
---

# Library Overview

litestar-asyncapi generates AsyncAPI 3.1 documents by default, with explicit 3.0 support, for Litestar applications (`litestar>=2.24.0`, tested on 2.24.0 and the latest 2.x)[^pkg]. Automatic discovery describes finalized WebSocket listeners, streams and actual ChannelsPlugin routes. Raw sockets require explicit payload metadata; non-WebSocket broker contracts use typed channel declarations. There is no automatic broker or SSE inference.

<!-- truth: start -->
- AsyncAPI 3.1.0 document generation by default with explicit 3.0.0 support; depends on `litestar>=2.24.0` with no upper cap.
- Automatic discovery for WebSocket listeners, streams, and ChannelsPlugin routes with include_in_schema checks.
- Native Litestar schema generator reuse with Draft07 wire export, preserving tuple bounds and recursion.
- Packaged documentation UI: Default AsyncAPI React 3.2.1; opt-in Scalar 1.69.2.
- WebSocket interactive console: Upstream advisory validation permitting intentional invalid payloads.
<!-- truth: end -->

Native Litestar schema plugins, DTO hooks, serialization, routing, static assets and CLI provide shared framework behavior. An isolated native schema registry and narrow compatibility/Draft07 adapters preserve tested tuple, alias, recursion and null contracts. AsyncAPI-specific models and assembly remain local. The public API is the package root export list[^api].

The plugins/ package owns one application plugin and browser adapters. Canonical documents are cached per app, protected by defensive copies and exposed through native JSON, optional YAML and headless CLI export. Security declarations describe contracts; they do not install runtime authorization.

Packaged AsyncAPI React component 3.2.1 is the default documentation renderer[^pkgjson]. Scalar 1.69.2 is opt-in because it omits positional tuple information, zero bounds and false payloads. Wheels include browser assets and licenses; consumers need neither Node nor a CDN.

Optional upstream asyncapi-ws-plugin 0.1.0 supports verified JSON-text object/array operations. It never auto-connects and uses advisory validation, intentionally allowing invalid sends. Unsupported modes retain documentation. Applications enforce actual payload and authorization rules.

Use official schema/parser gates, behavioral tests, real browser acceptance and installed-wheel Python 3.11–3.15 lanes as evidence. Do not equate nonempty output or successful documentation builds with complete schema or runtime fidelity.

[^pkg]: `pyproject.toml::project`
[^api]: `src/litestar_asyncapi/__init__.py`
[^pkgjson]: `package.json`
