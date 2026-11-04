---
type: Spec
flow_id: docs-redesign
title: Documentation Redesign on Zensical
description: Move the litestar-asyncapi docs from Sphinx to Zensical with task-oriented navigation, curated API reference, and every example executed in tests.
state: planned
parent_prd: null
research: []
plan_revision: 2
plan_commit: 23d1a4a
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [prd, docs, zensical, information-architecture]
---

# Documentation Redesign on Zensical

## 1. North Star Goal & Context

### Objectives

A new user can install the plugin, watch a document appear for their own WebSocket app, and find any public class in the reference within a few minutes, and every code sample on the site is known to run.

### Current State & Limits

- **Engine.** Sphinx with the `shibuya` theme (`docs/conf.py`). A manual strict build (`sphinx-build -W`, warning suppression cleared) is clean, but `make docs` does not run strict. The engine differs from the newer Litestar ecosystem sites, which use Zensical.
- **Thin guides.** The site has 876 lines of `.rst`, directives included. `docs/usage/quickstart.rst` is a six-line pointer to `docs/getting-started.rst`. No guide follows the "runnable example, then output, then walkthrough" pattern.
- **Oversized reference pages.** `docs/reference/*.rst` use `automodule :members: :undoc-members:`. The built `reference/spec.html` is 289 KB with 164 entries and `reference/core.html` is 205 KB. The `litestar-docs` budget is 120 KB and 14 outline items per page.
- **Unexecuted examples.** `docs/examples/**` is checked only for PEP 723 blocks and markers (`tools/ci/validate_pep723_blocks.py`, `tools/ci/validate_doc_markers.py`). No test imports or runs the apps.
- **No CLI reference.** `litestar asyncapi export` (`src/litestar_asyncapi/cli.py::register_commands`) has no reference page.
- **Tooling tied to Sphinx.** `tools/docs_audit.py` parses `.rst` files, and `tools/sphinx_ext/pygments_styles.py` exists only for Sphinx.

### What Is New & Why It Succeeds

- **Zensical engine.** Zensical + `mkdocstrings-python` (static Griffe analysis), set up as in the `litestar-docs` skill's Zensical architecture.
- **Four navigation tabs:**
  - **Learn**: setup, concepts, handlers, contracts, schemas, export.
  - **Integrations**: ChannelsPlugin, the documentation UI, security and servers, mounting.
  - **Reference**: curated API pages.
  - **Project**: migration, changelog, contributing.
- **Runnable examples first.** Each Learn page opens with an example that the test suite runs.

### Impact

- **Readers** get a site styled like the other Litestar ecosystem docs, with a right-hand outline and reference pages small enough to scan.
- **Maintainers** catch broken samples in `make test` instead of from user reports.

### Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Zensical is pre-1.0 (`0.0.x`). | Bound the version (`zensical>=0.0.71,<0.1`), lock it in `uv.lock`, and gate CI on the build plus `tools/docs/verify_docs_artifacts.py`. |
| Griffe reads source statically, so slotted dataclass fields without inline docstrings render empty. | Chapter 3 adds inline field docstrings to the public config, definition and spec classes, plus a scanner gate. |
| Old Sphinx URLs (`/getting-started.html`) break. | Chapter 2 locks the page map and emits flat `.html` redirect stubs that preserve the URL hash. |
| `main` deploys on every push, so a half-migrated site could go live. | Chapter 2 converts every page in full before removing Sphinx. Later chapters rewrite pages in place. |

### Success Metrics

- `zensical build --clean` exits `0`, and the artifact check passes.
- Every built Reference page is ≤ 120,000 bytes and has ≤ 14 outline items.
- Every module in `docs/examples/**` runs under `make test`, and its generated document passes `tools/validate_asyncapi.mjs`.
- No Learn page exceeds about 200 lines, and each one opens with an executed example.

## 2. Locked Architectural Decisions

1. **Engine: Zensical + mkdocstrings-python.** The user chose this.
   - Rejected: *Sphinx + litestar-sphinx-theme*. Smaller migration, but it keeps `.rst` and is out of step with the newer ecosystem sites.
   - Rejected: *keep Sphinx + shibuya*. It fixes nothing structural.
2. **Navigation: Learn / Integrations / Reference / Project.** The user chose this. The examples gallery moves under Learn.
   - Rejected: *a live Playground tab*. It would need the packaged UI embedded in a static site against a live server.
   - Rejected: *keep the current sections*.
3. **Hosting: GitHub Pages on `cofin/litestar-asyncapi`.**
   - `site_url = "https://cofin.github.io/litestar-asyncapi/"` and `repo_url = "https://github.com/cofin/litestar-asyncapi"`.
   - `pyproject.toml::project.urls` and the Codecov slug in `.github/workflows/ci.yml` point at `cofin`. These edits are in the working tree and not yet committed.
4. **Examples are apps, not scripts.** Every `docs/examples/**` module keeps its module-level `app: Litestar`, which the Litestar CLI runs.
   - In-process checks run in `src/tests/unit/docs/test_examples.py`.
   - Official schema validation runs in `make validate-asyncapi`, in the Node CI lane.
   - Rejected: the skill's `main()` convention, because these examples are servers, not one-shot scripts.
5. **Pages include whole example files** with `pymdownx.snippets`, with `check_paths = true` so a moved example fails the build. Markers would need inline comments, which the project bans.
6. **Reference pages are curated.** Each page has explicit `members:` lists under 2–5 H2 groups, `inherited_members: false` on leaf classes, and `show_bases: true`. The spec wire models are split across several pages.
7. **CLI reference is generated.** `tools/docs/generate_cli_docs.py` builds a group through `cli.py::register_commands` and renders it. `mkdocs-click` is not used, because it mis-renders defaults on Click ≥ 8.3.
8. **The Sphinx stack is removed after the new site builds, not before.** This covers `docs/conf.py`, `docs/Makefile`, `docs/make.bat`, `tools/sphinx_ext/`, the Sphinx dependencies and `.rst` sources.

## 3. Master Roadmap (Ordered Child Flows)

| Chapter | Flow ID | Title | Key Deliverables | Public Seams | Dependencies | State |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `docs-examples-verified` | Executed examples | Example tests, exported documents, official validation | `docs/examples/**::app`, `make validate-asyncapi` | none | draft |
| 2 | `docs-zensical-foundation` | Zensical site and full conversion | Config, full Markdown conversion at locked URLs, redirects, link checks, Sphinx removal | `make docs`, `.github/workflows/docs.yml` | none | draft |
| 3 | `docs-reference-curation` | Curated API reference | Reference pages within budget, field docstrings, scanner gate, CLI page | `src/litestar_asyncapi` public API | 2 (pages only) | draft |
| 4 | `docs-learn-content` | Learn and Integrations rewrite | Rewritten guides using the example-first structure, merged quickstart, examples gallery, migration/changelog/contributing in Markdown | `docs/**/*.md` | 1, 2, 3 | draft |

## 4. Global Constraints (Applicable to All Child Flows)

- Follow the `litestar-docs` skill's Zensical track:
  - `use_directory_urls = true`, `navigation.tabs`, `toc.follow`, `content.tabs.link`;
  - `enable_inventory = true` so `site/objects.inv` is produced;
  - the WCAG AAA neutral palette, with Litestar Gold reserved for logo, active tab and focus ring;
  - the light/dark hero switched with `[data-md-color-scheme]`, never `<picture>` media queries.
- Never hide the right-hand outline (`.md-sidebar--secondary`). Headings are unnumbered and contain no inline code.
- Keep Markdown tables to 2–4 columns, and never put `\|` inside backticked table cells.
- Examples keep PEP 723 blocks and contain no inline comments. `make validate-examples` and `make validate-pep723` keep passing.
- Write public prose in plain English, with no internal planning labels or ceremony.
- Python tools run through `uv run`, and new tooling lives under `tools/docs/`.
- Never use pytest fixtures inside `docs/examples/**`.

## 5. Backlog (Deferred Items)

- A live Playground tab that embeds the packaged AsyncAPI UI against a hosted demo server.
- A custom domain or a move to `litestar-org` hosting.
- Versioned docs, with a version switcher per release.
- TypeScript API docs for `tools/frontend/`.

## Implementation Plan

- [ ] docs-examples-verified — run every docs example app in pytest and validate its document (../docs-examples-verified/spec.md)
- [ ] docs-zensical-foundation — Zensical config, theme, build/CI/Pages wiring, redirects, Sphinx removal (../docs-zensical-foundation/spec.md)
- [ ] docs-reference-curation — budgeted API reference, field docstrings, scanner gate, CLI page (../docs-reference-curation/spec.md)
- [ ] docs-learn-content — example-first Learn/Integrations/Project pages (../docs-learn-content/spec.md)

## Continuity Snapshot

- **State:** planned. No child flow has started.
- **Decisions:** Zensical engine, four-tab navigation and `cofin` GitHub Pages hosting were chosen by the user on 2026-11-04. The hosting URLs are already updated in `pyproject.toml` and CI.
- **Review:** round 1 of the independent review is adjudicated. All 13 findings were adopted.
- **Discoveries:**
  - The installed-wheel lane copies only `src/tests`, so docs tests must skip when the checkout is absent.
  - Only `.github/workflows/distribution.yml` has Node.
  - The bug fixes in `../contract-fixes/spec.md` change visible output, which is why rendered fragments are generated rather than written.
