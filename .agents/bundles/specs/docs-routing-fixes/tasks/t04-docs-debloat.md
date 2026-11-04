---
type: Task
id: docs-routing-fixes:t04
title: Cache the UI manifest and skip a redundant document copy
state: completed
priority: P3
verification_strategy: characterization
depends_on: [t01, t02, t03]
files:
  - src/litestar_asyncapi/docs.py
  - src/litestar_asyncapi/plugins/core.py
tests:
  - src/tests/unit/test_ui_plugin.py
  - src/tests/integration/test_plugin_cache.py
plan_revision: 3
plan_commit: 91b5852
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:25:00Z
last_verified_commit: c1185d3
verification_evidence: "Baseline green: plugin_cache, routes, ui_plugin, ui_security, json_plugin, unit/plugins 32 passed. After: 33 passed (manifest read-once test added); make lint 0, make type-check 0, make test 0 (250 passed, 94.50%), make validate-asyncapi 0; docs.py 44% -> 46%, plugins/core.py 94% -> 94%"
created_at: 2026-11-04T18:17:00Z
updated_at: 2026-11-04T18:26:00Z
commit: c1185d3
tags: [debloat, docs-ui, cache]
---

# Cache the UI manifest and skip a redundant document copy

## Objective

Carry out the chapter 5 ledger rows: `_get_document` deep-copies the generated document only when `use_cache=True`, and `bootstrap_html` parses `manifest.json` once while keeping the `OSError`/`KeyError`/`ValueError` fallback. The per-request render copy and `_cached_json` stay (ledger *keep*).

## Context

- **Why `characterization`.** Behavior is unchanged; `test_all_document_accessors_are_defensive_and_clear_preserves_binding[False/True]` covers isolation with shared `Server` objects, and `test_missing_manifest_preserves_download_and_readable_error` covers the fallback.
- **Change.** `docs.py::_read_manifest` is an `lru_cache(maxsize=4)` keyed by manifest path; exceptions are not cached, so a missing manifest falls back on every request.

## Steps

1. Run the characterization set green.
2. Make the `_get_document` copy conditional; add `_read_manifest`.
3. Add `test_manifest_is_parsed_once_across_pages`.

## Verification

- **Initial:** characterization set 32 passed.
- **Final:** characterization set 33 passed; `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Uncached builds are copied once (by the public getter), cached builds keep the inner copy.
- [x] The manifest is read once across docs page requests; the missing-asset fallback still renders.
- [x] Ledger *keep* rows untouched.

## Notes & Discoveries

- [2026-11-04 18:25] `[tool.coverage.run] concurrency = ["multiprocessing"]` omits `thread`, so request-handler code in the TestClient portal thread (`bootstrap_html`, `_read_manifest`) is never traced. Total moved 94.53% -> 94.50% from one new untraced line; per-file coverage held or rose. Candidate for `test-gate-debloat`.
