---
type: Spec
flow_id: docs-examples-verified
title: Executed Documentation Examples
description: Run every docs example app under pytest, export its AsyncAPI document, and validate it with the official schemas in the Node CI lane.
state: completed
parent_prd: docs-redesign
research: []
plan_revision: 3
plan_commit: f70309e
state_revision: 0
current_task: null
last_verified_checkpoint: 5b81e9e
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T23:25:00Z
tags: [docs, examples, testing]
---

# Executed Documentation Examples

## Charter

Today `docs/examples/**` modules are checked for metadata blocks but never run. This flow makes three checks part of the normal gates:

- Every example's module-level `app` must start.
- Every example's app must serve its AsyncAPI document.
- That document must pass the official AsyncAPI schemas and parser.

## Upstream Dependencies

None. The flow does not depend on the docs engine.

## Key Deliverables

- **Example test.** `src/tests/unit/docs/test_examples.py` runs one test case per module from a glob over `docs/examples/**/*.py`, excluding `__init__.py`.
  - Each test case imports the module and opens `litestar.testing.TestClient(app)`.
  - The document URL comes from `app.route_reverse("asyncapi:json")`, so mounted examples such as `docs/examples/mounted_docs.py` need no hard-coded paths.
  - The test asserts a 200 response with `application/vnd.asyncapi+json`.
  - It finds the repository root from the test file's location. If `docs/examples/` is absent (the installed-wheel lane copies only `src/tests`), the whole module skips. If the directory exists but the glob is empty, the test fails.
- **Export tool.** `tools/docs/export_example_documents.py` writes each example's document to `docs/_generated/<example>.json`. `docs/_generated/` is git-ignored. Chapter 4 includes these files on the site, so the docs never show output written by hand.
- **Official validation.** `tools/validate_asyncapi.mjs` validates every file in `docs/_generated/`. `make validate-asyncapi` runs the export tool first. CI covers this through the existing Node lane, `make build js-test validate-asyncapi browser-test` in `.github/workflows/distribution.yml`.

## Public Seams

- `docs/examples/**::app`
- The `asyncapi:json` route name, reversed with `Litestar.route_reverse`
- `make validate-asyncapi`

## Acceptance Boundary

- `uv run pytest src/tests/unit/docs -q --no-cov` and `make validate-asyncapi` pass.
- `make installed-test` still passes, with the docs module skipped.
- Removing `app` from any example, or making its document invalid, fails one of the two gates.

## Implementation Plan

- [x] [1d12cee] t01 — serve the AsyncAPI document from every docs example in pytest (tasks/t01-example-app-tests.md)
- [x] [5b81e9e] t02 — export example documents to `docs/_generated/` and validate them in `make validate-asyncapi` (tasks/t02-export-and-validate.md)

**Recovery checkpoint:** `uv run pytest src/tests/unit/docs -q --no-cov && make check-all && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **State:** completed at `5b81e9e`. `make check-all` (275 passed, 96.68%), `make validate-asyncapi` (10 example documents) and `make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum` (264 passed, docs module skipped) exit `0`.
- **Discoveries:** `contracts.py` had its docs routes disabled and now serves them; `mounted_docs.py` needs its guard header in the test; the validator now expands directory arguments and rejects empty ones.
