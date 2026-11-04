---
title: Knowledge Base Index
description: Routing index for architecture, patterns, domains, testing, gotchas, decisions and workflow knowledge of litestar-asyncapi.
tags: [knowledge, asyncapi, litestar, index]
---

# Knowledge Base

<!-- truth: start -->
- Plugin lifecycle, docs routes, cache: [architecture/01](./architecture/01-system-overview.md), [patterns/plugin-architecture](./patterns/plugin-architecture.md).
- Document assembly, operation keys, `$ref` escaping: [architecture/02](./architecture/02-generator-pipeline.md), [patterns/schema-generation](./patterns/schema-generation.md).
- WebSocket and ChannelsPlugin discovery: [architecture/03](./architecture/03-discovery-and-extractors.md).
- Schema bridge and Draft07 export: [architecture/04](./architecture/04-schema-generation.md), [ADR-002](./decisions/adr-002-draft07-wire-dialect.md).
- Spec objects and serialization: [architecture/05](./architecture/05-spec-objects-and-serialization.md).
- Renderers, UI, interaction: [architecture/06](./architecture/06-render-plugins-and-ui.md), [patterns/renderer-security](./patterns/renderer-security.md).
- Vocabulary: [domains/asyncapi-contracts](./domains/asyncapi-contracts.md).
- Tests and seams: [testing/public-seam-tdd](./testing/public-seam-tdd.md); wheels/browsers: [testing/distribution-and-browser](./testing/distribution-and-browser.md).
- Footguns: [gotchas/runtime-and-tooling](./gotchas/runtime-and-tooling.md).
- CI and release: [patterns/ci-supply-chain](./patterns/ci-supply-chain.md).
- Commands and Flow loop: [workflow](./workflow.md).
<!-- truth: end -->

## Namespaces

| Namespace | Index | Scope |
| --- | --- | --- |
| Architecture | [architecture/index.md](./architecture/index.md) | Deep modules, seams and dataflow (chapters 01–06) |
| Patterns | [patterns/index.md](./patterns/index.md) | Reusable patterns and anti-patterns |
| Domains | [domains/index.md](./domains/index.md) | Ubiquitous glossary and lifecycle |
| Testing | [testing/index.md](./testing/index.md) | Test map and verification lanes |
| Gotchas | [gotchas/index.md](./gotchas/index.md) | Non-obvious traps |
| Decisions | [decisions/index.md](./decisions/index.md) | ADRs |
| Style guides | [styleguides/index.md](./styleguides/index.md) | Python and Bash style |
| Workflow | [workflow.md](./workflow.md) | Canonical commands and Flow execution |

Documentation artifacts and legacy links: [testing/documentation-site](./testing/documentation-site.md).
