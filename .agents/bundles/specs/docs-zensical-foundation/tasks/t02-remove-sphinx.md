---
type: Task
id: docs-zensical-foundation:t02
title: Remove the Sphinx stack and the marker validator
state: completed
priority: P2
verification_strategy: characterization
depends_on: [t01]
files:
  - docs/conf.py
  - docs/Makefile
  - docs/make.bat
  - docs/_static/style.css
  - docs/examples/README.md
  - docs/examples/index.rst
  - docs/**/*.rst
  - tools/sphinx_ext/
  - tools/build_docs.py
  - tools/docs_audit.py
  - tools/ci/validate_doc_markers.py
  - Makefile
  - pyproject.toml
  - README.md
  - .github/workflows/ci.yml
  - .agents/bundles/knowledge/workflow.md
tests:
  - tools/docs/verify_docs_artifacts.py
plan_revision: 3
plan_commit: 992aefc
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T00:40:00Z
last_verified_commit: b5db0c7
verification_evidence: "Before and after: make docs 0 (no issues, 24 redirects, 47 pages). After: make check-all 0 (275 passed, 96.68%), make validate-asyncapi 0, make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum 0 (264 passed, 1 skipped), make zizmor 0."
created_at: 2026-11-04T23:40:00Z
updated_at: 2026-11-05T00:40:00Z
commit: b5db0c7
tags: [docs, cleanup]
---

# Remove the Sphinx stack and the marker validator

## Objective

Delete the Sphinx configuration, `.rst` sources, Sphinx helpers and the `validate-examples` marker gate once the Zensical site builds, leaving the site output unchanged.

## Context

- **Why `characterization`.** Deletion with unchanged site output: the same `make docs` result before and after.
- **Invariants.** Master Decision 8. `docs/__init__.py` and `docs/examples/__init__.py` stay because the CLI commands load `docs.examples.*` modules.
- **Canonical surface.** `make docs`, `make lint`.

## Steps

1. Delete the Sphinx files, `tools/sphinx_ext/`, `tools/build_docs.py`, `tools/docs_audit.py`, `docs/examples/README.md` and `tools/ci/validate_doc_markers.py`.
2. Drop the `validate-examples` target, its lint dependency and CI step, and the `docs/conf.py` ruff exemption.
3. Point README links at the published site; refresh workflow commands, tech stack and release-ci skill guidance.

## Verification

- **Final:** `make docs`, `make check-all`, `make validate-asyncapi` and `make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum` exit `0`.

## Acceptance Criteria

- [x] No Sphinx file, dependency or target remains.
- [x] The site builds and verifies exactly as before the deletion.

## Notes & Discoveries

- [2026-11-05 00:35] `.agents` guidance that named `validate-examples`, `docs_audit.py` or Sphinx now names the example test, the export tool, Zensical and lychee.
