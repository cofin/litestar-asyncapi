---
type: Task
id: docs-examples-verified:t02
title: Export docs example documents and validate them with the official schemas
state: completed
priority: P1
verification_strategy: static_validation
depends_on: [t01]
files:
  - tools/docs/__init__.py
  - tools/docs/export_example_documents.py
  - tools/validate_asyncapi.mjs
  - Makefile
  - .gitignore
tests:
  - tools/validate_asyncapi.mjs
plan_revision: 3
plan_commit: f70309e
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T23:25:00Z
last_verified_commit: 5b81e9e
verification_evidence: "make validate-asyncapi 0 on Node 26 (10 example documents validated). Probes: invalid operation action exit 1 (official-schema/oneOf), empty directory exit 1, example without app exit 1 (TypeError). make check-all 0 (275 passed)."
created_at: 2026-11-04T23:00:00Z
updated_at: 2026-11-04T23:25:00Z
commit: 5b81e9e
tags: [docs, examples, tooling]
---

# Export docs example documents and validate them with the official schemas

## Objective

`tools/docs/export_example_documents.py` writes each example's canonical document to the git-ignored `docs/_generated/<example>.json`, and `make validate-asyncapi` exports them and validates the directory with `tools/validate_asyncapi.mjs`.

## Context

- **Why `static_validation`.** Tooling and gate wiring; proven by isolated violations.
- **Invariants.** Node runs only in `.github/workflows/distribution.yml`, which already calls `make validate-asyncapi`; no workflow change is needed.
- **Canonical surface.** `Makefile::validate-asyncapi`, `Makefile::export-example-documents`.

## Steps

1. Implement the export tool through `AsyncAPIPlugin.get_asyncapi_json`, recreating the output directory each run.
2. Let `validate_asyncapi.mjs` expand directory arguments and reject an empty directory.
3. Wire `export-example-documents` into `validate-asyncapi` and ignore `docs/_generated/`.

## Verification

- **Final:** `make validate-asyncapi` and `make check-all` exit `0`; each probe exits `1`.

## Acceptance Criteria

- [x] Every example document is written to `docs/_generated/` and passes the official schemas and parser.
- [x] An invalid document, an empty directory and an example without `app` each fail the gate.

## Notes & Discoveries

- [2026-11-04 23:20] Output names: `channels_plugin/app.py` becomes `channels_plugin.json`, `contracts.py` becomes `contracts.json`.
