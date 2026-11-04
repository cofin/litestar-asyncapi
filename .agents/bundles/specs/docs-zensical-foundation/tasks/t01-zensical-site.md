---
type: Task
id: docs-zensical-foundation:t01
title: Build the site with Zensical at locked URLs with redirects and artifact verification
state: completed
priority: P1
verification_strategy: documentation_validation
depends_on: []
files:
  - zensical.toml
  - lychee.toml
  - docs/index.md
  - docs/learn/
  - docs/integrations/
  - docs/project/
  - docs/reference/
  - docs/stylesheets/extra.css
  - tools/docs/postbuild.py
  - tools/docs/verify_docs_artifacts.py
  - Makefile
  - pyproject.toml
  - uv.lock
  - .gitignore
  - .github/workflows/ci.yml
  - .github/workflows/docs.yml
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
last_verified_at: 2026-11-05T00:30:00Z
last_verified_commit: 9dde341
verification_evidence: "Baseline: Sphinx build. After, in a fresh worktree of 9dde341: make docs 0 (zensical --strict 'No issues found', 24 redirect stubs, verifier across 47 pages), make validate-examples validate-pep723 0, pytest 275 passed. Probes: missing snippet path exit 2, broken Markdown anchor exit 2 (strict), injected broken link and anchor exit 1, missing stub exit 1, missing objects.inv exit 1. Playwright: usage/websocket-handlers.html#server-sent-events lands on learn/websocket-handlers/#server-sent-events. make zizmor 0."
created_at: 2026-11-04T23:40:00Z
updated_at: 2026-11-05T00:30:00Z
commit: 9dde341
tags: [docs, zensical, ci]
---

# Build the site with Zensical at locked URLs with redirects and artifact verification

## Objective

`make docs` builds every former page, converted in full to Markdown at its locked URL, with zero warnings; writes hash-preserving redirect stubs for every former Sphinx URL; and verifies `site/objects.inv`, the stubs and every internal link and anchor. CI publishes `site/` and checks external links with a SHA-pinned lychee action.

## Context

- **Why `documentation_validation`.** Engine, content and gate change; proven by the strict build, the verifier and isolated probes.
- **Invariants.** Master Decisions 1, 3, 5 and 8; global constraints on outline visibility, headings without code, 2–4 column tables, snippets with `check_paths = true`, and the neutral palette with gold reserved for logo, active tab and focus ring.
- **Canonical surface.** `Makefile::docs`, `tools/docs/verify_docs_artifacts.py::main`, `tools/docs/postbuild.py::REDIRECTS`.

## Steps

1. Lock Zensical, mkdocstrings-python and pymdown-extensions in the docs group; write `zensical.toml` and `docs/stylesheets/extra.css`.
2. Convert every page in full under the four tabs; include whole example files with snippets; keep the gallery's former section anchors.
3. Add `tools/docs/postbuild.py` and `tools/docs/verify_docs_artifacts.py`; rewire `make docs`, `docs-serve`, `docs-linkcheck`, `docs-clean`, `.github/workflows/docs.yml` and the `build-docs` job.

## Verification

- **Initial:** `make docs` runs the Sphinx build.
- **Final:** `make docs` and `make zizmor` exit `0`; each probe exits non-zero; a redirect stub keeps its fragment in Chromium.

## Acceptance Criteria

- [x] Every former page's content is present in Markdown at its locked URL.
- [x] Every former Sphinx URL has a stub that resolves and keeps the URL fragment.
- [x] The strict build reports no issues; `objects.inv` exists; internal links and anchors resolve.
- [x] CI publishes `site/` and runs lychee from a pinned SHA; zizmor is clean.

## Notes & Discoveries

- [2026-11-04 23:45] Zensical 0.0.74 (latest; `<0.1` bound kept) and mkdocstrings-python 2.0.10 require Python 3.11+, while the project supports 3.10. The docs group carries `python_version >= '3.11'` markers and `make docs` runs in a separate `.venv-docs` on `DOCS_PYTHON` (default 3.12), so the 3.10 development environment is untouched. pymdown-extensions resolves to 12.3.
- [2026-11-04 23:50] `zensical build --strict` fails on missing snippet paths and broken Markdown links or anchors, so the verifier's link check mainly guards theme output and redirect stubs.
- [2026-11-05 00:00] Built reference pages are over budget (`core` 208 KB, `spec` 332 KB); budgets are chapter 3's gate.
- [2026-11-05 00:10] lychee is not installed locally and could not be fetched in this environment; `make docs-linkcheck` printed its skip message and the CI step's arguments are unexercised. `lychee.toml` limits checks to http(s) and excludes the not-yet-deployed site URL and bare font hosts.
- [2026-11-05 00:15] Former labels on the examples gallery (`#decorator-overrides` and others) are kept as heading ids so old deep links still land on their section.
