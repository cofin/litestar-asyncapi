---
type: Spec
flow_id: docs-examples-verified
title: Executed Documentation Examples
description: Run every docs example app under pytest, export its AsyncAPI document, and validate it with the official schemas in the Node CI lane.
state: draft
parent_prd: docs-redesign
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
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
