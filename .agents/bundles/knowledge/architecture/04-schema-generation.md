---
type: Guide
title: "Architecture 04: Schema Generation & Registry"
description: Native Litestar schema generation, isolated registry finalization and Draft07 export.
tags: [architecture, schema, type-system, registry, plugins]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: sg
    resource: src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator
    title: Per-build schema generator
  - id: compat
    resource: src/litestar_asyncapi/_compat.py::create_schema_creator
    title: Native SchemaCreator bridge
  - id: dialect
    resource: src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema
    title: Draft07 dialect adapter
---

# Architecture 04: Schema Generation & Registry

AsyncAPISchemaGenerator delegates Python type evaluation[^sg] to Litestar >=2.24.0 without an upper bound limit. App-provided OpenAPI schema plugins participate even when OpenAPI serving is disabled.

## Compatibility Boundary

All private Litestar imports are isolated in _compat.py.[^compat] Each build uses a fresh native SchemaCreator and SchemaRegistry, independent of the app's OpenAPI cache. The installed supported version is authoritative; sibling checkout hooks may differ.

Narrow corrections preserve fixed and empty tuple cardinality, msgspec array-like wire order/default tails, Python 3.10 nested generic forward references and explicit null presence. User schema-plugin overrides retain precedence. Tuple bounds intersect declared constraints; bare and variadic tuples remain unbounded. Array-like Struct minimum length follows the last required wire position, and extra items remain permitted unless the model forbids them.

Standard-library annotation resolution uses owner-module and app signature namespaces without changing globals. Unresolved references fail with payload/handler context. Native spec objects use a lossless projection that preserves null-valued dictionaries; explicit field and schema_extra null defaults/consts are tracked. Bare native Schema(default=None/const=None) cannot reveal whether None was explicitly supplied.

## Registry Finalization

Native registration handles recursive models and name collisions. generate() retains native roots and returns mutable raw schemas. components() finalizes native names and refreshes previously returned dictionaries so early references remain correct after later same-name registrations. Finalize before serializing the document. Never share the app OpenAPI registry or eagerly freeze provisional reference names.

## Draft07 Export Boundary

Litestar's OpenAPI engine generates JSON Schema Draft 2020-12 schemas. However, AsyncAPI 3.0 and 3.1 native Schema Objects and official tooling (@asyncapi/specs, @asyncapi/parser, and React/Scalar UI) mandate JSON Schema Draft 07 semantics.

The dialect adapter acts as a lossless bridge[^dialect]: it traverses schema positions only, converts modern tuple (prefixItems -> items arrays + minItems/maxItems), dependency, and definition constructs, preserves literal data, and rewrites moved local references. Empty fixed tuples use maxItems:0, not invalid items:[].

Implicit modern/2020-12 input preserves sibling constraints by wrapping references in allOf. Explicit Draft07 retains its own reference semantics. Unsupported declared dialects, nested ID scopes, mixed dialects and unsupported modern keywords raise path-specific diagnostics. Explicit MultiFormatSchema values bypass native conversion.

## Verification

Use `uv run pytest <path> -q --no-cov` for focused runs, make test, make type-check, make slotscheck and Node 22 make validate-asyncapi. Behavioral coverage checks actual recursive reference targets, custom app plugins, model aliases/tags, tuple and array-like decoder contracts, null constraints and OpenAPI-state isolation. Nonempty output alone does not prove schema fidelity.

[^sg]: `src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator`
[^compat]: `src/litestar_asyncapi/_compat.py::create_schema_creator`
[^dialect]: `src/litestar_asyncapi/asyncapi/schema_generation/dialect.py::to_asyncapi_schema`
