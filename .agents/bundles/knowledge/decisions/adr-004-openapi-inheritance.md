---
type: Decision
title: ADR-004 OpenAPI Contract Inheritance
description: Lazy metadata and security inheritance with explicit WebSocket server isolation.
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
  - id: openapi
    resource: src/litestar_asyncapi/asyncapi/openapi.py
    title: Metadata and security translation
  - id: gen
    resource: src/litestar_asyncapi/asyncapi/generator.py::_populate_channels
    title: Server isolation guard
---

# ADR-004 OpenAPI Contract Inheritance

## Context

Litestar applications already configure metadata and authentication schemes in OpenAPI. Duplicating them creates conflicting documents, while HTTP security requirements and server URLs cannot be copied without changing their transport meaning.

## Decision

Read app.openapi_config lazily at AsyncAPI build time and inherit only unset metadata and mappable security scheme definitions.[^openapi] Explicit AsyncAPI values win. Tags and security requirements remain explicit. inherit_openapi disables all inheritance.

Server inheritance is separately opt-in. Derived ws/wss servers bind discovered WebSockets only. Reject a mixed document when any unrelated channel lacks an explicit nonempty server list, since an omitted or empty list means all servers.[^gen]

## Alternatives Rejected

Requiring duplicate metadata avoids automatic defaults but increases drift. Copying app.openapi_schema adds generation and shared-state coupling. Copying HTTP security requirements loses alternatives and exclusions. Silently skipping derived servers obscures requested behavior; empty channel lists cannot isolate them.

## Consequences

Default document titles may change with application metadata. Unmappable schemes warn and skip. Mixed-transport applications opting into derived servers must declare complete explicit contracts for unrelated channels. Errors expose ambiguity before clients consume a misleading contract.

[^openapi]: `src/litestar_asyncapi/asyncapi/openapi.py`
[^gen]: `src/litestar_asyncapi/asyncapi/generator.py::_populate_channels`
