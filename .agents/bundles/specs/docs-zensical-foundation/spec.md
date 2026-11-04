---
type: Spec
flow_id: docs-zensical-foundation
title: Zensical Site Foundation
description: Replace the Sphinx build with Zensical, convert all existing pages to Markdown at locked URLs, and wire build, link checks, redirects and Pages deployment.
state: completed
parent_prd: docs-redesign
research: []
plan_revision: 3
plan_commit: 992aefc
state_revision: 0
current_task: null
last_verified_checkpoint: b5db0c7
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-05T00:40:00Z
tags: [docs, zensical, build, ci]
---

# Zensical Site Foundation

## Charter

Replace the Sphinx build with a Zensical site that deploys to `https://cofin.github.io/litestar-asyncapi/`.

- **Navigation.** Four tabs: Learn, Integrations, Reference and Project.
- **Content.** Every existing page is converted in full to Markdown, not left as a stub, so the site deployed from `main` never loses content.
- **URLs.** Page URLs are locked here and do not change in later chapters. Chapter 4 rewrites pages in place.
- **Sphinx removal.** The Sphinx stack is deleted in the same flow, once the Zensical build passes.

## Upstream Dependencies

None.

## Key Deliverables

- **`zensical.toml`** at the repository root:
  - `site_url` set to the Pages URL, `repo_url = "https://github.com/cofin/litestar-asyncapi"`, and `use_directory_urls = true`.
  - Features: `navigation.tabs`, `toc.follow`, `content.tabs.link` and `content.code.copy`.
  - `pymdownx.snippets` with `check_paths = true`, and `pymdownx.superfences` with mermaid.
  - `mkdocstrings` with `enable_inventory = true` and the Litestar inventory `https://docs.litestar.dev/latest/objects.inv`.
- **Dependencies.** In `pyproject.toml::dependency-groups.docs`, replace the Sphinx packages with `zensical>=0.0.71,<0.1`, `mkdocstrings-python>=2.0.1` and `pymdown-extensions>=10.16`, and lock them.
- **Locked page map.** Write this table into the spec when the flow is planned. Rules:
  - `getting-started` and the six-line `usage/quickstart` merge into `learn/installation`.
  - Every other `.rst` page converts one-to-one under its tab.
  - `migration`, `changelog` and `contribution-guide` move to `project/`, converted in full.
- **Reference placeholders.** Reference pages exist from day one, with one `:::` module page each, until chapter 3 curates them.
- **Theme and assets.** `docs/stylesheets/extra.css` uses the neutral palette and sidebar widths from the `litestar-docs` skill (its Zensical architecture and information-architecture guides). `docs/index.md` gets a light/dark hero switched with `[data-md-color-scheme]`, reusing `docs/_static/logo-light.svg` and `docs/_static/logo-dark.svg`.
- **Examples on pages.** Pages include whole example files, with the PEP 723 header kept, because it shows the dependencies.
- **Retire the marker validator.** No example contains `# start-example` markers, so `tools/ci/validate_doc_markers.py` currently checks nothing. Delete it along with its `validate-examples` Make target and CI step.
- **`tools/docs/postbuild.py`** writes flat `.html` redirect stubs that preserve the URL hash, from every former Sphinx URL to its entry in the locked page map.
- **`tools/docs/verify_docs_artifacts.py`** checks three things:
  - `site/objects.inv` exists and is not empty.
  - Every redirect stub resolves.
  - Every internal link and anchor in `site/**/*.html` resolves.

  Chapter 3 adds page-size budgets.
- **External link check.** External links are checked by `lychee`, run from a pinned-SHA action in `.github/workflows/ci.yml::build-docs`. `make docs-linkcheck` runs `lychee` against `site/`, and skips with a message when `lychee` is not installed.
- **Build commands and CI.**
  - `make docs` runs the build, postbuild and verify steps. `make docs-serve` and `make docs-clean` are updated to Zensical.
  - `.github/workflows/docs.yml` uploads `site/`.
  - `tools/build_docs.py` is replaced by `make docs`.
- **Delete the Sphinx stack:** `docs/conf.py`, `docs/Makefile`, `docs/make.bat`, `docs/_static/style.css`, `tools/sphinx_ext/`, `tools/build_docs.py`, `tools/docs_audit.py` with its `docs-audit` Make target, `docs/examples/README.md` (superseded by the Learn examples gallery), and all `.rst` sources.

## Public Seams

- `make docs`
- `make docs-linkcheck`
- `.github/workflows/docs.yml`
- `site/objects.inv`

## Acceptance Boundary

- On a clean checkout, `make docs` builds with zero warnings and `verify_docs_artifacts.py` passes.
- Every former Sphinx URL redirects to its locked page.
- Every former page's content is present in Markdown.

## Locked Page Map

URLs are relative to `https://cofin.github.io/litestar-asyncapi/`. Later chapters rewrite these pages in place and never move them. Each former page gets a flat redirect stub from `tools/docs/postbuild.py::REDIRECTS` that keeps the URL fragment.

| Former Sphinx page | Locked page | Tab |
| --- | --- | --- |
| `index.html` | `/` (`docs/index.md`) | Home |
| `usage/index.html` | `learn/` | Learn |
| `getting-started.html`, `usage/quickstart.html` | `learn/installation/` | Learn |
| `usage/concepts.html` | `learn/concepts/` | Learn |
| `usage/websocket-handlers.html` | `learn/websocket-handlers/` | Learn |
| `usage/decorators.html` | `learn/decorators/` | Learn |
| `usage/schema-generation.html` | `learn/schema-generation/` | Learn |
| `examples/index.html`, `examples/README.html` | `learn/examples/` | Learn |
| none (new section index) | `integrations/` | Integrations |
| `usage/channels-plugin.html` | `integrations/channels-plugin/` | Integrations |
| `usage/renderers.html` | `integrations/documentation-ui/` | Integrations |
| `usage/security-and-servers.html` | `integrations/security-and-servers/` | Integrations |
| `reference/index.html`, `reference/api.html`, `genindex.html`, `py-modindex.html` | `reference/` | Reference |
| `reference/core.html` | `reference/core/` | Reference |
| `reference/plugins.html` | `reference/plugins/` | Reference |
| `reference/spec.html` | `reference/spec/` | Reference |
| `reference/extractors.html` | `reference/extractors/` | Reference |
| `reference/schema-generation.html` | `reference/schema-generation/` | Reference |
| none (new section index) | `project/` | Project |
| `migration.html` | `project/migration/` | Project |
| `changelog.html` | `project/changelog/` | Project |
| `contribution-guide.html` | `project/contribution-guide/` | Project |
| `search.html` | `/` | Home |

`reference/index.html` is served by the new page itself, so it needs no stub. The gallery keeps its former section ids (`#websocket-listener`, `#decorator-overrides`, ...).

## Implementation Plan

- [x] [9dde341] t01 — Zensical site at locked URLs with full Markdown conversion, redirect stubs, artifact verification and CI wiring (tasks/t01-zensical-site.md)
- [x] [b5db0c7] t02 — remove the Sphinx stack and the marker validator (tasks/t02-remove-sphinx.md)

**Recovery checkpoint:** `make docs && make check-all && make validate-asyncapi && make zizmor` exits `0`.

## Continuity Snapshot

- **State:** completed at `b5db0c7`. `make docs` (strict build with no issues, 24 redirect stubs, verifier across 47 pages), `make check-all` (275 passed, 96.68%), `make validate-asyncapi`, `make zizmor` and `make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=minimum` exit `0`.
- **Decisions:** Zensical 0.0.74 within `>=0.0.71,<0.1`; mkdocstrings-python 2.0.10; pymdown-extensions 12.3. These need Python 3.11+, so the docs group is marker-gated and `make docs` builds in `.venv-docs` on `DOCS_PYTHON=3.12`.
- **Discoveries:** reference pages exceed the 120 KB budget (`core` 208 KB, `spec` 332 KB) until chapter 3; lychee was not run locally, so the CI step is unexercised; the migration page still says SSE inference is unsupported, which predates SSE discovery and is left for chapter 4.
