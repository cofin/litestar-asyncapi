---
type: Index
title: Flow Specifications Index
description: Current and completed Flow specifications and task worksheets.
tags: [specs, flows, worksheets, index]
---

# Flow Specifications

Active and planned Flow specifications and task worksheets.

| Flow | Type | State | Parent | Summary |
| --- | --- | --- | --- | --- |
| [docs-redesign](./docs-redesign/spec.md) | PRD | planned | — | Move docs to Zensical with task-oriented navigation and executed examples. |
| [docs-examples-verified](./docs-examples-verified/spec.md) | Flow | draft | docs-redesign | Run every docs example app in pytest and validate its document. |
| [docs-zensical-foundation](./docs-zensical-foundation/spec.md) | Flow | draft | docs-redesign | Zensical config, theme, build/CI/Pages wiring, redirects, Sphinx removal. |
| [docs-reference-curation](./docs-reference-curation/spec.md) | Flow | draft | docs-redesign | Budgeted API reference, field docstrings, scanner gate, CLI page. |
| [docs-learn-content](./docs-learn-content/spec.md) | Flow | draft | docs-redesign | Example-first Learn, Integrations and Project pages. |
| [contract-fixes](./contract-fixes/spec.md) | PRD | completed | — | Fix verified contract, discovery and routing bugs; remove leaked internals; debloat tests and gates. |
| [public-hygiene](./public-hygiene/spec.md) | Flow | completed | contract-fixes | Remove leaked internals, green lint. |
| [wire-contract-fixes](./wire-contract-fixes/spec.md) | Flow | completed | contract-fixes | Alias-driven wire keys, prefixItems export, conformance fixture. |
| [schema-fixes](./schema-fixes/spec.md) | Flow | completed | contract-fixes | Tuple, bounds, example and null fidelity. |
| [discovery-fixes](./discovery-fixes/spec.md) | Flow | completed | contract-fixes | Listener naming, metadata order, decorator merging, discovery debloat. |
| [docs-routing-fixes](./docs-routing-fixes/spec.md) | Flow | completed | contract-fixes | Single-plugin guard, root path, console unions, caching. |
| [test-gate-debloat](./test-gate-debloat/spec.md) | Flow | completed | contract-fixes | Trim tests and gates with proven replacements. |
| [realtime-discovery](./realtime-discovery/spec.md) | PRD | completed | — | Issue #11: transport markers, SSE discovery, typed ChannelsPlugin topics. |
| [channel-source-markers](./channel-source-markers/spec.md) | Flow | completed | realtime-discovery | x-litestar-source and ws bindings on discovered channels. |
| [sse-discovery](./sse-discovery/spec.md) | Flow | completed | realtime-discovery | Server-Sent Event route discovery. |
| [channels-plugin-topics](./channels-plugin-topics/spec.md) | Flow | completed | realtime-discovery | Topic-only discovery and channel_payloads. |

Completed flows are recorded in [bundles/log.md](../log.md).
