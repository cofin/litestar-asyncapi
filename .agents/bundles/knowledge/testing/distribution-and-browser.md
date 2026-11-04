---
type: Guide
title: Distribution, Installed-Wheel and Browser Lanes
description: How built wheels, packaged UI assets and official AsyncAPI tooling are verified outside the checkout.
tags: [testing, distribution, playwright, installed-wheel, asyncapi-parser]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: inst
    resource: Makefile::installed-test
    title: Installed-wheel lane
  - id: val
    resource: tools/validate_asyncapi.mjs
    title: Official schema/parser gate
  - id: pw
    resource: playwright.config.ts
    title: Playwright configuration
  - id: binst
    resource: Makefile::browser-test-installed
    title: Installed browser lane
  - id: srv
    resource: tools/frontend/tests/server.py
    title: Browser test server
---

# Distribution, Installed-Wheel and Browser Lanes

Commands live in [Project workflow](../workflow.md); this page records what each lane proves.

<!-- truth: start -->
- Node (`.nvmrc`) is build/test-only: `make js-install build` produces assets, wheel and sdist; consumers need neither Node nor a CDN.
- `make validate-asyncapi` validates an exported fixture with the pinned official parser, spec schemas and Draft07 payload checks.
- `make js-test browser-test` runs Vitest and Playwright against the source tree; artifacts go to `.tmp/test-results`.
- `make installed-test PYTHON_VERSION=3.1x [LITESTAR_BOUNDARY=latest]` tests the built wheel outside the checkout on 3.10–3.14.
- `make browser-test-installed PYTHON_VERSION=3.12` compares installed and source manifest hashes before opening the packaged UI.
- Nonempty output or a successful docs build is not evidence of schema or runtime fidelity.
<!-- truth: end -->

## Installed-wheel lane

`installed-test` copies `src/tests` into a temp directory, creates a fresh venv, installs the wheel with `litestar==2.24.0` (minimum) or `litestar>=2.24,<3` (`LITESTAR_BOUNDARY=latest`), asserts the import resolves inside the venv's site-packages and that a minimal app emits `asyncapi: 3.1.0`, then runs the full suite[^inst]. Repin the minimum after locked test dependencies change; resolve latest separately and do not resync the lock afterwards.

Missing PyYAML fails Litestar import itself; disabled YAML routes are the supported negative case.

## Official validation

`tools/validate_asyncapi.mjs` validates the exported fixture and `src/tests/fixtures/asyncapi/*.json` against `@asyncapi/specs` and `@asyncapi/parser`[^val]. Record known upstream parser discrepancies rather than claiming universal format support.

## Browser acceptance

Playwright covers generated 3.0/3.1 documents, recursive references, tuple/null/false/header content, hostile metadata, external-network blocking, malformed documents, missing assets, CSP fallbacks, and interactive valid/invalid frames, reconnects and page-departure cleanup[^pw]. The browser test server runs under `uvicorn`[^srv]; the installed lane adds `uvicorn` and `websockets` to the temporary venv[^binst]. Normal pages require zero browser errors and zero external requests.

[^inst]: `Makefile::installed-test`
[^val]: `tools/validate_asyncapi.mjs`
[^pw]: `playwright.config.ts`
[^binst]: `Makefile::browser-test-installed`
[^srv]: `tools/frontend/tests/server.py`
