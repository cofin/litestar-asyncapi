---
type: Decision
title: "ADR-002: Draft07 wire dialect"
description: Native AsyncAPI 3.0/3.1 payload schemas are exported as Draft07 with annotation-derived tuple bounds.
tags: [decisions, adr, draft07, schema, tuples]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: dialect
    resource: src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema
    title: Draft07 dialect adapter
  - id: val
    resource: tools/validate_asyncapi.mjs
    title: Official schema/parser gate
---

# ADR-002: Draft07 wire dialect

**Status:** Accepted (2026-09-20). Replaces the earlier `prefixItems`-on-wire invariant.

## Context

Litestar generates JSON Schema 2020-12. Native AsyncAPI 3.0/3.1 Schema Objects, `@asyncapi/specs`, `@asyncapi/parser` and the React/Scalar renderers use Draft07 semantics, so 2020-12 tuple keywords are silently ignored on the wire.

## Decision

Keep Litestar's internal representation and translate only schema positions at export[^dialect]. Emit tuple `items` arrays with annotation-derived `minItems`/`maxItems`; empty fixed tuples use `maxItems: 0`. Explicit null and literal data survive. Unsupported semantic conversion fails with a schema path instead of weakening contracts. Explicit `MultiFormatSchema` remains available to bypass conversion.

## Consequences

- Generated documents validate against pinned official tooling[^val].
- Some 2020-12 constructs cannot be expressed and raise diagnostics rather than degrade.
- Fixed tuple length cannot be inferred from `prefixItems` alone; the compat bridge must read the annotation.

[^dialect]: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema`
[^val]: `tools/validate_asyncapi.mjs`
