---
type: Guide
title: Runtime and Tooling Gotchas
description: Non-obvious footguns in tests, Litestar integration, schema generation, UI parsing and release tooling.
tags: [gotchas, pytest, litestar, tooling, release]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-completion
    at: 2026-11-04
    commit: dcc21c01b0e1e0bad5f4547dad61f075364629c2
sources:
  - id: addopts
    resource: pyproject.toml::tool.pytest.ini_options
    title: Global coverage addopts
  - id: bind
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin._get_document
    title: One-app binding
  - id: future
    resource: pyproject.toml::tool.ruff.lint.flake8-tidy-imports.banned-api
    title: Future-annotations ban
  - id: bump
    resource: pyproject.toml::tool.bumpversion
    title: Release bump configuration
  - id: sg
    resource: src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator.components
    title: Registry finalization
  - id: boot
    resource: src/litestar_asyncapi/docs.py::bootstrap_html
    title: Manifest lookup
---

# Runtime and Tooling Gotchas

<!-- truth: start -->
- Focused `uv run pytest <path>` exits 1 from the global `--cov-fail-under=80`; add `--no-cov`.
- `from __future__ import annotations` is rejected repo-wide by ruff TID251; Litestar resolves real annotations at runtime.
- One `AsyncAPIPlugin` instance serves one app; a second app raises `ImproperlyConfiguredException`, even after `clear_cache()`.
- Call `AsyncAPISchemaGenerator.components()` before serializing; early `$ref` dicts are refreshed in place.
- Litestar 2.24 arbitrary-ASGI mounts drop the stripped prefix from `root_path`; documented, not worked around.
- `make release` bumps versions only (`commit = false`, `tag = false`) despite its help text mentioning a tag.
<!-- truth: end -->

## Testing

- **Coverage floor on partial runs.** `addopts` carries `--cov=litestar_asyncapi --cov-fail-under=80`[^addopts]. Any single-file run reports ~40% and exits 1, so its exit code cannot distinguish red from green. Use `--no-cov`.
- **`make_dataclass` module names.** On Python 3.12+, `make_dataclass` overrides a `__module__` supplied through the namespace. Assign `__module__` after construction when tests need distinct module-qualified names across 3.11–3.15.

## Litestar integration

- **App binding.** `_get_document` binds the first app it sees and rejects any other[^bind]. Tests that build several apps need one plugin per app.
- **Future annotations.** Ruff's `banned-api` (TID251) fails any file containing the import[^future]; string annotations would break native signature and schema resolution.
- **PyYAML.** Litestar 2.24 imports PyYAML itself. YAML routes are opt-in via `DocsConfig.yaml`; do not add a local extra or presence check.
- **Arbitrary ASGI mounts.** Native Router nesting and correct `root_path` produce right URLs; arbitrary ASGI mounting in Litestar 2.24 does not accumulate the prefix. Do not add a second URL resolver.

## Schema generation

- **Provisional reference names.** Native registration may rename components when later same-name models arrive. `components()` finalizes names and refreshes dicts returned earlier[^sg]; never freeze names eagerly or share the app OpenAPI registry.
- **Bare `None` defaults.** A native `Schema(default=None)` cannot reveal whether `None` was explicit. Explicit null defaults/consts are tracked separately through the compat bridge.

## UI and assets

- **Manifest keys.** `bootstrap_html` looks up `tools/frontend/<entry>.ts`, falling back to `frontend/<entry>.ts`[^boot]. Missing or stale assets render a JSON-download alert instead of failing the route. Rebuild with `make build` after frontend changes.
- **Upstream parser defects.** The pinned parser misreads literal `$ref` data and drops own `__proto__` keys; the React view protects and restores them around `Parser.parse`. Canonical downloads are never rewritten.

## Release

- **No tagging.** `[tool.bumpversion]` sets `commit = false` and `tag = false`[^bump]; `make release bump=…` edits versions, docs and lock only. Tags and pushes remain explicit, user-initiated actions.

## Discovery and examples

- Topic names are native callback identities, not normalized URL suffixes. Read generated_channels_topic before applying channel_payloads.
- Arbitrary ChannelsPlugin subscriptions mutate native topic mappings. Keep initialization snapshots; never publish runtime subscriptions.
- Omitted or empty channel servers means all document servers. Derived WebSocket servers require explicit servers on unrelated channels.
- Optional payload examples read outer-field declarations first, then the non-null model. Import ExampleFactory only when generation is requested; minimal package imports must not require Pydantic.
- Explicit Schema references use final Draft07 wire keys, even when prefix_items is supplied as a convenience.

[^addopts]: `pyproject.toml::tool.pytest.ini_options`
[^bind]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin._get_document`
[^future]: `pyproject.toml::tool.ruff.lint.flake8-tidy-imports.banned-api`
[^bump]: `pyproject.toml::tool.bumpversion`
[^sg]: `src/litestar_asyncapi/asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator.components`
[^boot]: `src/litestar_asyncapi/docs.py::bootstrap_html`
