---
type: Index
title: Architecture Knowledge Index
description: Living system architecture chapters for litestar-asyncapi.
tags: [architecture, asyncapi, litestar, index]
---

# Architecture Knowledge

Living system architecture chapters for `litestar-asyncapi`.

| Chapter | Title | Description |
| --- | --- | --- |
| [01. System Overview](./01-system-overview.md) | `Guide` | Plugin lifecycle, InitPluginProtocol, docs router mounting, and caching |
| [02. Generator Pipeline](./02-generator-pipeline.md) | `Guide` | Document assembly, Info, Servers, operation-key casefolding uniqueness, and RFC 6901 JSON pointer escaping |
| [03. Discovery & Extractors](./03-discovery-and-extractors.md) | `Guide` | WebSocket handler inference (listener, stream, raw), include_in_schema check, and ChannelsPlugin deduplication |
| [04. Schema Generation & Registry](./04-schema-generation.md) | `Guide` | Native Litestar schema plugins, isolated registry finalization and Draft07 tuple export |
| [05. Spec Objects & Serialization](./05-spec-objects-and-serialization.md) | `Guide` | Slotted dataclasses, BaseSchemaObject recursive serialization, slotscheck, and AsyncAPI 3.0/3.1 entities |
| [06. Render Plugins & UI Security](./06-render-plugins-and-ui.md) | `Guide` | JSON, YAML, AsyncAPI UI, Interactive Playground, and XSS sanitization |
