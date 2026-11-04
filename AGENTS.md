# Project Instructions for AI Agents

This project uses **Flow** with **Open Knowledge Format (OKF v0.2)** bundles under `.agents/bundles/` for planning, specification, architecture and task tracking.

## Context Pointers

- **Bundle root:** `.agents/bundles/index.md`
- **Knowledge routing:** `.agents/bundles/knowledge/index.md`
- **Workflow & canonical commands:** `.agents/bundles/knowledge/workflow.md`
- **Project skills & subagents:** `.agents/skills/index.md` — before changing or reviewing code, load the engineering skill for the touched domain (`asyncapi-generation`, `asyncapi-schema`, `asyncapi-docs-ui`, `asyncapi-release-ci`) and its `review-*` skill when reviewing. Paired reviewer/specialist subagents live in `.agents/agents/`.
- **Footguns:** `.agents/bundles/knowledge/gotchas/runtime-and-tooling.md`
- **Active specs:** `.agents/bundles/specs/<flow_id>/`; `tasks/*.md` are the single authority for task state; `/flow:sync` reconciles `spec.md`.
- **History:** `.agents/bundles/log.md`

## Build & Test Commands

Prefer `Makefile` targets. Run Python tools via `uv run`.

```bash
make install                                   # uv sync --all-extras --dev
uv run pytest src/tests/path.py -q --no-cov    # focused test; --no-cov is required (global 80% floor fails partial runs)
make test                                      # full suite with coverage floor
make lint                                      # prek, type-check, slotscheck, zizmor, validate-examples, validate-pep723
make type-check                                # mypy src && pyright
make fix                                       # ruff autofix + format
make check-all                                 # lint, test-all, coverage

make docs docs-linkcheck                       # Sphinx build and link check

# Packaged frontend and installed distribution (Node 22 for build/tests only)
make js-install build                          # locked npm install, assets, wheel and sdist
make validate-asyncapi                         # official schema/parser and exported fixture
make js-test browser-test                      # Vitest and real Chromium tests
make installed-test PYTHON_VERSION=3.12
make browser-test-installed PYTHON_VERSION=3.12
```

## Architecture Overview

`litestar-asyncapi` generates AsyncAPI 3.1 documents (explicit 3.0 support) and hosts documentation for Litestar applications:

1. **AsyncAPIPlugin (`plugins/core.py`):** `InitPluginProtocol` with `__slots__`; `on_app_init` mounts the isolated docs router (`create_docs_router()`); owns the per-app canonical document cache.
2. **Configuration (`config.py`):** Slotted `AsyncAPIConfig` (metadata, channel contracts, uniqueness) and nested `DocsConfig` (endpoints, guards, dependencies, render plugins).
3. **AsyncAPIGenerator (`asyncapi/generator.py`):** Discovery, channel/operation/schema resolution, and finalization of an isolated native schema registry.
4. **Extractors (`asyncapi/extractors/`):** `websocket.py` walks finalized route trees honoring `include_in_schema`; `channels.py` reads `ChannelsPlugin` routes with deduplication.
5. **Schema generation (`asyncapi/schema_generation/`):** Native Litestar `SchemaCreator` and per-build registry through `_compat.py`, lossless Draft07 export, application schema plugins.
6. **Spec objects (`spec/`):** Slotted dataclasses on `BaseSchemaObject` implementing AsyncAPI 3.0/3.1 entities.
7. **Render plugins (`plugins/`):** Native Litestar JSON/YAML renderers and renderer base; AsyncAPI UI adapters in `plugins/renderers.py`.

## Conventions & Patterns

- **Python:** >= 3.10, PEP 604 unions, PEP 585 collections. No `from __future__ import annotations` in package code.
- **No inline comments:** explanations belong in Google-style docstrings.
- **Slotted classes:** enforced via `slotscheck`; owned UI adapters inheriting unslotted native renderer bases are narrowly exempt.
- **Tuple fidelity:** fixed-length tuples keep positional types and exact length; wire output uses Draft07 `items` arrays with `minItems`/`maxItems`. Never infer length from `prefixItems` alone.
- **Operation identity:** case-insensitive uniqueness with `.casefold()`; no wire `operationId`.
- **Renderer security:** `html.escape(..., quote=True)` for dynamic attributes; inert JSON protected against script-tag closure; `textContent` for plain DOM messages; keep hostile-input browser regressions.
- **Native reuse:** use Litestar renderers, serialization, `Empty`, routing, static assets and CLI before adding equivalent local code.
- **Interactive console:** React default, Scalar opt-in with known limits; interaction is opt-in with upstream advisory validation that permits intentional invalid sends. No second validator or transport.
