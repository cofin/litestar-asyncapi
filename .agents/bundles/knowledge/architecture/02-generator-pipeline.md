---
type: Guide
title: "Architecture 02: Document Generator Pipeline"
description: Complete document assembly process in AsyncAPIGenerator from discovery to components resolution.
tags: [architecture, generator, pipeline, assembly]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-completion
    at: 2026-11-04
    commit: dcc21c01b0e1e0bad5f4547dad61f075364629c2
sources:
  - id: gen
    resource: src/litestar_asyncapi/asyncapi/generator.py::AsyncAPIGenerator
    title: Document assembly
  - id: uniq
    resource: src/litestar_asyncapi/asyncapi/generator.py::_ensure_unique_operation_id
    title: Operation-map identity
  - id: ds
    resource: src/litestar_asyncapi/asyncapi/datastructures.py::ChannelDefinition
    title: Shared typed contracts
---

# Architecture 02: Document Generator Pipeline

`AsyncAPIGenerator` orchestrates the extraction, schema conversion, and assembly[^gen] of the root `AsyncAPI` 3.x specification document.

## Generation Pipeline Flow

```
1. Initialize Schema Engine
   ├── AsyncAPISchemaGenerator (type parsing)
   └── Native Litestar SchemaRegistry (deduplication under #/components/schemas/)

2. Construct Root Document
   ├── Info (explicit values, then OpenAPI metadata, then defaults)
   ├── Default Content Type (omitted unless explicitly configured)
   └── Servers (explicit config plus opt-in derived WebSocket servers)

3. Channel Discovery (_discover_channels)
   ├── Extract WebSocket channels (extract_websocket_channels)
   ├── Extract ChannelsPlugin routes and configured topics
   └── Extract SSE routes (extract_sse_channels)

4. Populate Document Channels & Operations
   ├── Map DiscoveredChannel -> Channel (address, parameters, messages)
   ├── Map DiscoveredOperation -> Operation (action, channel ref, messages)
   ├── Sanitize operation-map identity and enforce uniqueness (.casefold())
   └── Escape JSON Pointer tokens (~ to ~0, / to ~1)

5. Populate Components
   ├── Register reusable operation and message traits
   └── AsyncAPISchemaGenerator.components() (native naming finalization + Draft07 projection)
```

## Operation ID Uniqueness & Strict Mode

To ensure full compatibility with enterprise code generators and rigid validators:
- `_ensure_unique_operation_id` evaluates `candidate.casefold()`[^uniq] against all registered IDs and dictionary keys.
- If an operation ID collision occurs:
  - When `config.strict_uniqueness` is `False`: Appends an incrementing suffix (starting at `_2`).
  - When `config.strict_uniqueness` is `True`: Raises `litestar.exceptions.ImproperlyConfiguredException`.

## RFC 6901 JSON Pointer Escaping

All internal `$ref` targets (such as `#/channels/{channel_id}` or `#/components/messages/{message_id}`) must escape characters per RFC 6901:
- `~` is escaped to `~0`
- `/` is escaped to `~1`
- The escaped token is then percent-encoded (`urllib.parse.quote(..., safe="~")`) so braces and other URI-unsafe characters form a valid URI fragment.

This ensures that parameterized channel addresses like `/ws/{room_id:str}` form valid JSON Pointer reference strings.

## Shared typed contract boundary

MessageDefinition, OperationDefinition and ChannelDefinition are shared by decorators and explicit AsyncAPIConfig.channels entries.[^ds] Internal channel/operation subclasses add provenance only; no separate discovered-message DTO exists. Python payload types and FieldDefinition values survive discovery and become schemas and normalized MessageExample values during assembly. Multiple named messages remain operation-specific choices. Explicit empty message/example lists override inference; None denotes no override.

Explicit channel keys identify documents independently from transport addresses. A configured key replaces matching inference; distinct keys may share an address. Conflicting explicit keys identify both configuration sources. Two discovered channels with the same key raise and identify both sources; conflicting schemas/examples identify both sources. Assembly orders encoded contracts deterministically and indexes casefolded keys. Explicit config.components merge without overwriting native schemas. Local reference checks validate known AsyncAPI/schema positions and selected-channel membership through aliases; literal data and external references are not traversed as document references.

Documentation settings reside in config.docs (DocsConfig). Provenance subclasses declare only their own slots explicitly.

## OpenAPI inheritance and named references

asyncapi/openapi.py reads only app.openapi_config at document-build time. It fills unset Info fields and merges mappable security scheme definitions without mutating the config or building app.openapi_schema. Tags and security requirements never inherit. inherit_openapi=False disables inheritance; unmappable schemes and relative OAuth URLs warn and skip.

Opt-in inherit_openapi_servers derives ws/wss servers from absolute HTTP URLs. Only discovered WebSockets receive those defaults. Every unrelated channel needs explicit nonempty servers when derived servers exist; [] also means all root servers. Conflicting inherited names fail with both sources. These behaviors are owned by AsyncAPIGenerator.build_asyncapi and _populate_channels.[^gen]

_resolve_names validates security and server names against final maps; _resolve_operation_traits and _resolve_message_traits resolve trait names. ReplyDefinition resolves channel/message membership after all operation message keys exist. Bare strings in list-valued name fields raise at construction.[^ds]

[^gen]: `src/litestar_asyncapi/asyncapi/generator.py::AsyncAPIGenerator`
[^uniq]: `src/litestar_asyncapi/asyncapi/generator.py::_ensure_unique_operation_id`
[^ds]: `src/litestar_asyncapi/asyncapi/datastructures.py::ChannelDefinition`
