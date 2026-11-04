---
okf_version: "0.2"
type: Index
title: Knowledge Bundles Index
description: Root index of litestar-asyncapi OKF v0.2 bundles.
tags: [index, okf, bundles]
---

# Knowledge Bundles Index

<!-- truth: start -->
- Python >= 3.10, run everything through `uv run`; PEP 604/585 typing; zero inline comments; no `from __future__ import annotations` in package code.
- Litestar `>=2.24.0` with no upper cap; private Litestar imports only in `_compat.py`.
- AsyncAPI 3.1.0 default, explicit 3.0.0; Draft07 payload schemas with annotation-derived tuple bounds.
- Operation identity is the casefold-unique operations-map key; no wire `operationId`.
- Escape dynamic HTML with `html.escape(..., quote=True)`; inert bootstrap JSON with `<` escaped; `textContent` for plain messages.
- Focused tests: `uv run pytest <path> -q --no-cov`; aggregate: `make check-all`.
- Project skills: [`../skills/index.md`](../skills/index.md).
<!-- truth: end -->

## Bundles

| Bundle | Purpose | Index |
| --- | --- | --- |
| Product | Definition, guidelines, technology stack | [product/index.md](./product/index.md) |
| Knowledge | Architecture, patterns, domains, testing, gotchas, decisions, workflow | [knowledge/index.md](./knowledge/index.md) |
| Research | Un-promoted research notes | [research/index.md](./research/index.md) |
| Specs | Active and planned Flow specifications | [specs/index.md](./specs/index.md) |
| Log | Append-only change log | [log.md](./log.md) |
