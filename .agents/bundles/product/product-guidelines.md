---
type: Guide
title: Product Guidelines & Engineering Standards
description: Deep-module seams, cold-reader documentation, code quality and commit conventions for litestar-asyncapi.
tags: [product, guidelines, standards, quality, documentation]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: api
    resource: src/litestar_asyncapi/__init__.py
    title: Public seam
  - id: compat
    resource: src/litestar_asyncapi/_compat.py
    title: Adapter boundary
  - id: ex
    resource: docs/examples
    title: Runnable documentation examples
  - id: prt
    resource: .github/workflows/pr-title.yml
    title: Conventional PR titles
---

# Product Guidelines & Engineering Standards

<!-- truth: start -->
- Deep modules: small public interfaces (`AsyncAPIPlugin`, `AsyncAPIConfig`, `DocsConfig`, definitions, decorators) hide discovery, schema and assembly internals.
- Seams: the package root export list is the public seam; `_compat.py` is the only adapter onto private Litestar APIs; the dialect adapter is the only 2020-12→Draft07 bridge.
- Reuse native Litestar behavior before adding local code; own only AsyncAPI semantics.
- Zero inline comments in Python; Google-style docstrings (`Args:`, `Returns:`, `Raises:`) explain usage, not history.
- Validate 3.0/3.1 output with pinned official schemas/parser; record upstream discrepancies instead of claiming universal support.
- Cold-reader docs: a reader with no context can run every example; examples import, construct and generate their documents.
- Commits and PR titles use `<type>(<scope>): <summary>`; describe only the change.
<!-- truth: end -->

## Deep modules and seams

| Module | Interface | Hidden implementation | Adapter |
| --- | --- | --- | --- |
| Plugin | `AsyncAPIPlugin`, `get_asyncapi*`, `clear_cache` | caching, app binding, normalization | native `Router`, renderers |
| Generator | `AsyncAPIGenerator.build_asyncapi` | discovery merge, identity, reference validation | — |
| Schema | `AsyncAPISchemaGenerator.generate` / `components` | native registry, null tracking, tuple bounds | `_compat.py`[^compat], dialect |
| UI | `AsyncAPIUIRenderPlugin`, `DocsConfig` | bootstrap HTML, assets, manifest | upstream React/Scalar/ws plugin |

Dependency categories: in-process (generator, spec, dialect), local-substitutable (Litestar app, `ChannelsPlugin`, test clients), remote-owned (upstream UI packages, PyPI publishing), external boundary (official AsyncAPI tooling, browsers). Breaking the root export list[^api] is a public API change.

## Documentation

- Sphinx autodoc reference from docstrings; every public method and config field documented.
- Runnable examples under `docs/examples/` with PEP 723 metadata[^ex]; compile/metadata gates do not prove execution.
- Conceptual diagrams use Mermaid with 4–6 nodes.
- Prose is present tense and states current behavior; history belongs in the changelog.

## Quality

- Explicit type guards and actionable, path-specific error messages.
- Core modules (`asyncapi/`, `spec/`, `plugins/`) target >90% coverage.
- PR titles are validated against conventional-commit format[^prt].

[^api]: `src/litestar_asyncapi/__init__.py`
[^compat]: `src/litestar_asyncapi/_compat.py`
[^ex]: `docs/examples`
[^prt]: `.github/workflows/pr-title.yml`
