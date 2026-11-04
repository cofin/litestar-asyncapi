---
type: Guide
title: Technology Stack
description: Verified languages, frameworks, runtimes and test/lint toolchain for litestar-asyncapi.
tags: [product, tech-stack, python, litestar, uv, asyncapi]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: pkg
    resource: pyproject.toml
    title: Python build, dependencies and tool configuration
  - id: pkgjson
    resource: package.json
    title: Frontend build and validation toolchain
  - id: vite
    resource: vite.config.ts
    title: UI asset build
  - id: make
    resource: Makefile
    title: Command surface
---

# Technology Stack

<!-- truth: start -->
- Python >= 3.10 (CI 3.10–3.14); PEP 604 unions and PEP 585 collections; no `from __future__ import annotations` in package code.
- Litestar `>=2.24.0`, no upper cap; CI tests the 2.24.0 minimum and latest `<3`.
- Serialization through Litestar `encode_json`/`decode_json` with application type encoders; PyYAML arrives transitively from Litestar.
- `uv` for environments and running tools; `hatchling` build backend; `bump-my-version` for releases.
- `ruff` lint/format via `prek`; `mypy` and `pyright` strict; `slotscheck` for slot integrity.
- `pytest` + `pytest-cov` (aggregate floor 80%, core target >90%); coverage traces `multiprocessing` and `thread`.
- Docs: Sphinx with the Shibuya theme, `auto-pytabs`, `sphinx-design`; runnable PEP 723 examples.
- Node (`.nvmrc`) build/test only: Vite, Vitest, Playwright/Chromium, `@asyncapi/parser` + `@asyncapi/specs` + AJV.
- UI pins: AsyncAPI React 3.2.1, Scalar 1.69.2, asyncapi-ws-plugin 0.1.0 on React 18.3.1.
<!-- truth: end -->

## Python package

`pyproject.toml` is authoritative for dependencies, tool settings, the pytest coverage floor and the slotscheck exclusion list[^pkg]. Private Litestar imports are isolated in `src/litestar_asyncapi/_compat.py`.

## Browser and distribution

`package.json` pins every UI and validator package; `npm ci` against `package-lock.json` keeps builds reproducible[^pkgjson]. Separate Vite entries compile `tools/frontend/react.ts` and `tools/frontend/scalar.ts` into `src/litestar_asyncapi/assets/ui/`[^vite]. Wheels ship the hashed assets, manifest and licenses, so consumers need neither Node nor a CDN. Release and CI consume the same tested distribution artifact built by `make build`[^make].

[^pkg]: `pyproject.toml`
[^pkgjson]: `package.json`
[^vite]: `vite.config.ts`
[^make]: `Makefile`
