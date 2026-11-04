---
type: Spec
flow_id: docs-reference-curation
title: Curated API Reference
description: Budgeted mkdocstrings reference pages, inline field docstrings for public classes, a docstring scanner gate and a generated CLI page.
state: draft
parent_prd: docs-redesign
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [docs, reference, docstrings, cli]
---

# Curated API Reference

## Charter

Replace the blanket `automodule` dumps with curated reference pages. Each page is within 120 KB of HTML and has at most 14 outline items. Every public configuration, definition and spec field is documented by an inline docstring that Griffe can read.

## Upstream Dependencies

- `docs-zensical-foundation`: provides the Reference tab, mkdocstrings and `verify_docs_artifacts.py`. The docstring and scanner work does not need the new engine and can start earlier.

## Key Deliverables

- **Reference pages under `docs/reference/`**, each with explicit `members:` lists under 2–5 H2 groups:
  - `plugin.md`: `AsyncAPIPlugin`, `AsyncAPIConfig`, `DocsConfig`.
  - `contracts.md`: `asyncapi_operation`, `asyncapi_message`, `ChannelDefinition`, `OperationDefinition`, `MessageDefinition`.
  - `generator.md`: `AsyncAPIGenerator` and the extractors.
  - `schema.md`: the schema generation and dialect export entry points.
  - `renderers.md`: the JSON/YAML renderers and the UI render plugins.
  - `spec/document.md`: AsyncAPI, Info, Server and Components.
  - `spec/channels.md`: Channel, Parameter, Operation and Reply.
  - `spec/messages.md`: Message, traits, Schema and MultiFormatSchema.
  - `spec/bindings-security.md`: bindings and security schemes.
  - `cli.md`: the export command.
- **Leaf classes** use `inherited_members: false` and `show_bases: true`. `BaseSchemaObject` is documented once.
- **Inline docstrings.** Add a PEP 257 docstring directly below every public `@dataclass` field that lacks one, in:
  - `DocsConfig` in `src/litestar_asyncapi/config.py` (`AsyncAPIConfig` already has them);
  - `src/litestar_asyncapi/asyncapi/datastructures.py`;
  - `src/litestar_asyncapi/spec/**`.
- **Docstring gate.** `tools/docs/scan_public_docstrings.py` is an AST scanner for public `@dataclass` classes. It fails when any field lacks an inline docstring, and when a public docstring contains an internal planning label. There are no `TypedDict`, `msgspec.Struct` or `@overload` targets in the package, so those checks are left out. It is wired into `make lint`. Before relying on it, prove the gate against a deliberately broken fixture.
- **Page budgets.** `tools/docs/verify_docs_artifacts.py` gains the checks that each Reference page is at most 120,000 bytes and has at most 14 outline items.
- **CLI page.** `tools/docs/generate_cli_docs.py` builds a `click.Group`, calls `src/litestar_asyncapi/cli.py::register_commands` with a default `AsyncAPIPlugin()`, and renders the resulting `asyncapi export` command into `docs/reference/cli.md` at build time.

## Public Seams

The public API exported from `src/litestar_asyncapi/__init__.py` and `src/litestar_asyncapi/spec/__init__.py`.

## Acceptance Boundary

The scanner exits `0`, `verify_docs_artifacts.py` reports every Reference page within budget, and `make lint` and `make type-check` stay green.
