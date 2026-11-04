---
type: Decision
title: "ADR-001: Native Litestar ownership"
description: Reuse Litestar schema plugins, renderers, serialization, routing, static serving and CLI; own only AsyncAPI semantics.
tags: [decisions, adr, litestar, native-reuse]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: core
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin
    title: Native plugin, router and cache
  - id: compat
    resource: src/litestar_asyncapi/_compat.py
    title: Private Litestar import boundary
  - id: dep
    resource: pyproject.toml::project.dependencies
    title: Litestar dependency bound
---

# ADR-001: Native Litestar ownership

**Status:** Accepted (2026-09-20)

## Context

Earlier custom type plugins repeated alias, inheritance and recursion defects that Litestar's own schema engine already handles. A greenfield rewrite would discard useful metadata and discovery without gaining a native AsyncAPI implementation.

## Decision

Use Litestar for schema plugins, DTO hooks, JSON/YAML renderers, serialization, `Empty`, routing, static serving and CLI loading[^core]. Keep AsyncAPI models, document assembly and narrow regression-backed compatibility/dialect adapters. Isolate every private Litestar import in `_compat.py`[^compat]. Declare `litestar>=2.24.0` with no upper cap[^dep]; CI tests the 2.24.0 minimum and the latest `<3` release. A plugin belongs to one app, with private canonical caches and defensive public copies. Clean import and configuration breaks were approved with migration documentation.

## Consequences

- Upstream fixes flow in automatically; upstream private-API changes surface in one module.
- The no-cap bound trades resolver freedom for downstream apps against the risk of an untested Litestar 3 install.
- Local duplicates of native renderers, serializers or registries are rejected in review.

[^core]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin`
[^compat]: `src/litestar_asyncapi/_compat.py`
[^dep]: `pyproject.toml::project.dependencies`
