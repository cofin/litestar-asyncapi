---
type: Spec
flow_id: docs-routing-fixes
title: Docs Routing and Console
description: Reject a second AsyncAPIPlugin, reject a root docs path, handle object unions in the console, and cache the UI manifest.
state: draft
parent_prd: contract-fixes
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
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
