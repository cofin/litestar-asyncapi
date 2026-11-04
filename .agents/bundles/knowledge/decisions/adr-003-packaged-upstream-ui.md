---
type: Decision
title: "ADR-003: Packaged upstream UI and advisory interaction"
description: Ship pinned AsyncAPI React (default) and Scalar (opt-in) in the wheel, with opt-in advisory WebSocket interaction.
tags: [decisions, adr, ui, react, scalar, interaction]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: rend
    resource: src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin
    title: Packaged UI renderer
  - id: vite
    resource: vite.config.ts
    title: Build-time asset bundling
  - id: ws
    resource: tools/frontend/interactive.ts
    title: Interactive console adapter
---

# ADR-003: Packaged upstream UI and advisory interaction

**Status:** Accepted (2026-09-20)

## Context

Documentation must render offline from the wheel, without Node or a CDN at runtime. Scalar 1.69.2 renders AsyncAPI natively but failed positional tuple, zero-bound and false-payload cases.

## Decision

Default to AsyncAPI React component 3.2.1 on React 18.3.1[^rend]. Keep Scalar 1.69.2 as explicit opt-in with a visible limitation notice. Bundle locked assets and licenses into the wheel at build time with Vite[^vite]; no runtime Vite or Node dependency. A disposable public-parser adapter protects literal data against verified upstream parser defects; canonical downloads stay unchanged. Use asyncapi-ws-plugin 0.1.0 for opt-in JSON-text object/array interaction[^ws]. Validation is advisory and intentionally permits invalid sends; no automatic connections and no second transport or validator.

## Consequences

- Wheels carry hashed JS/CSS and a manifest that browser lanes compare across source and installed copies.
- Upgrading a UI pin requires rebuilding assets and rerunning browser acceptance.
- Applications remain responsible for payload validation and authorization.

[^rend]: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin`
[^vite]: `vite.config.ts`
[^ws]: `tools/frontend/interactive.ts`
