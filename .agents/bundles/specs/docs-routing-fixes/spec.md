---
type: Spec
flow_id: docs-routing-fixes
title: Docs Routing and Console
description: Reject a second AsyncAPIPlugin, reject a root docs path, handle object unions in the console, and cache the UI manifest.
state: completed
parent_prd: contract-fixes
research: []
plan_revision: 3
plan_commit: 91b5852
state_revision: 0
current_task: null
last_verified_checkpoint: c1185d3
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T18:30:00Z
tags: [docs-ui, routing, security]
---

# Docs Routing and Console

## Charter

Close the docs-page cross-linking exposure (audit B3), along with the remaining docs-routing and console defects. Domain skill: `asyncapi-docs-ui`. Review with `review-asyncapi-docs-ui`.

## Upstream Dependencies

- `public-hygiene`.

## Key Deliverables

- **B3.** `AsyncAPIPlugin.on_app_init` raises `ImproperlyConfiguredException` when `app_config.plugins` holds another `AsyncAPIPlugin` (`plugin is not self`), naming both docs paths. It raises whether or not docs are enabled. Test it in `src/tests/integration/test_routes.py`.
- **B12.** `DocsConfig.__post_init__` rejects any path that normalizes to the root (`"/"`, `""`, `"//"`).
- **B13 (code reading only).** Reproduce it first in `tools/frontend/interactive.test.ts`. If it reproduces, `supportsWire` accepts a `type` array with no scalar members and `oneOf`/`anyOf` whose members are all objects. If it does not reproduce, close the item with the test as evidence.
- **Debloat** (the Master ledger rows assigned to chapter 5):
  - Skip the `deepcopy` in `_get_document` only when `use_cache=False`. It stays whenever caching is on.
  - Cache the parsed manifest in `docs.py::bootstrap_html`, keeping the fallback on `OSError`, `KeyError` and `ValueError`.
- **Rebuild assets** if any frontend source changes. Packaged assets under `src/litestar_asyncapi/assets/ui/` must match a Node (`.nvmrc`) rebuild.

## Public Seams

- `AsyncAPIPlugin`
- `DocsConfig`
- The docs routes
- `tools/frontend/interactive.ts::supportsWire`

## Acceptance Boundary

- `make test`, `make js-test` and `make browser-test` pass.
- Two plugins in one app fail at startup with a clear message.

## Implementation Plan

- [x] [3defa63] t01 — reject a second `AsyncAPIPlugin` on one application (tasks/t01-single-plugin-guard.md)
- [x] [5b8d84c] t02 — reject a docs path at the application root (tasks/t02-root-docs-path.md)
- [x] [bb88760] t03 — open the console for nullable objects and object unions (tasks/t03-console-object-unions.md)
- [x] [c1185d3] t04 — cache the UI manifest and skip a redundant document copy (tasks/t04-docs-debloat.md)

**Recovery checkpoint:** `make lint && make type-check && make test && make validate-asyncapi && make js-test && make browser-test` exits `0`.

## Continuity Snapshot

- **State:** completed. All four tasks landed; `make lint`, `make type-check`, `make test` (250 passed, 94.50%) and `make validate-asyncapi` exit `0` at `c1185d3`; `make js-test` (12) and `make browser-test` (19, Chromium) exit `0` with Node 26.
- **B13** reproduced in Vitest and was fixed; packaged assets were rebuilt with Node 26 after confirming HEAD rebuilt byte-identically.
- **Discoveries:**
  - Coverage omits the `thread` concurrency, so request-handler code is never traced (`docs.py` reports 46%). Candidate for `test-gate-debloat`.
  - A `oneOf` with a `{type: null}` member still declines the console; only `type` arrays may carry `null`.
