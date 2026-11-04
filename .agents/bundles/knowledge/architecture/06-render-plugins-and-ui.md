---
type: Guide
title: "Architecture 06: Render Plugins and UI"
description: Native renderer ownership, packaged browser rendering and canonical document fidelity.
tags: [architecture, renderers, ui, security]
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
  - id: docs
    resource: src/litestar_asyncapi/docs.py::bootstrap_html
    title: Inert bootstrap HTML
  - id: fe
    resource: tools/frontend/view.ts
    title: React view adapter
---

# Render Plugins and UI

The plugins/ package separates application lifecycle[^rend] in core.py from AsyncAPI browser adapters in renderers.py.

JSON and YAML renderers are native Litestar JsonRenderPlugin and YamlRenderPlugin. AsyncAPIRenderPlugin is the native OpenAPIRenderPlugin base. DocsConfig supplies AsyncAPI paths and media types. Direct native renderer construction retains its native defaults. YAML routes are opt-in; current Litestar requires PyYAML transitively.

The application plugin normalizes documents with Litestar serialization and application encoders. Renderers receive equivalent normalized values, preserving literal nulls and custom examples. Inert bootstrap JSON uses native encode_json with closing-tag protection[^docs]; HTML attributes use html.escape. Each plugin belongs to one app. Private canonical caches are protected by defensive copies; clear_cache and use_cache=False preserve ownership.

## Packaged documentation

AsyncAPI React component 3.2.1 is the default. Scalar 1.69.2 is opt-in and displays a limitation notice because it omits positional tuple information, zero bounds and false payloads. All TypeScript UI source code, Vitest unit tests, and Playwright browser integration tests reside in `tools/frontend/`, keeping the repository root strictly organized. Playwright test output artifacts are directed to `.tmp/test-results` so test runs leave no untracked artifacts.

Separate Vite entries (`tools/frontend/react.ts` and `tools/frontend/scalar.ts`) compile into `src/litestar_asyncapi/assets/ui/`. Wheel/sdist include hashed JS/CSS, manifest and licenses; consumers need neither Node nor a CDN. Native static routing serves stable filesystem resources without temporary extraction. Zip imports are unsupported explicitly.

The React view unwraps recognized Draft07 MultiFormat schema envelopes[^fe], adapts boolean schemas to equivalent object schemas and remaps affected references. Canonical JSON/YAML downloads remain unchanged. The pinned parser misinterprets literal $ref data and loses own __proto__ keys: a reversible disposable protection pass uses public Parser.parse and restores its public document.json graph before handing the parsed interface to React. This protects literal data and map keys without replacing the upstream parser.

Browser acceptance covers generated 3.0/3.1 documents, recursive references, tuple/null/false/header content, hostile metadata, external-network blocking, malformed documents, missing assets, restrictive CSP fallbacks and a wheel installed outside the checkout. Source and installed manifests must match. Normal pages require zero browser errors/external requests.

## Routing and interaction boundary

Named native routes supply downloads, docs and static assets with inherited guards/dependencies and reversed URLs. DocsConfig.enabled controls installation. Native Router nesting and correct accumulated ASGI root_path pass; Litestar 2.24 arbitrary-ASGI mounting omits the stripped prefix from root_path. Preserve this limitation rather than implementing a second URL resolver.

The optional console uses pinned asyncapi-ws-plugin 0.1.0 through its public operation slot. DocsConfig.interactive is the single switch for default React interaction and the named console route; supplied renderers retain their explicit settings. Scalar links to the same React console.

The console never auto-connects. Upstream validation is advisory: users can deliberately send schema-invalid JSON or malformed text, with a visible notice. Frames preserve original textarea text; application-side validation remains authoritative. Gate interaction to explicit JSON-text object/array contracts, including reply messages. Unsupported modes retain documentation and a readable notice. Explicit ws/wss servers and resolved parameters are required; URL editing is disabled.

Real browser acceptance covers valid and invalid frames, authentication rejection/reconnect, shared connection lifetime, page departure cleanup, mount prefixes, and CSP connection refusal. WSS URL resolution is tested, but no live TLS endpoint was used. Both source and installed-wheel browser suites pass 19 cases; the isolated runner needs uvicorn plus websockets. Native public ws:status events clear stale connection alerts after a successful reconnect. Page departure unmounts the upstream component; persisted pageshow reloads after BFCache restoration.

[^rend]: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin`
[^docs]: `src/litestar_asyncapi/docs.py::bootstrap_html`
[^fe]: `tools/frontend/view.ts`
