---
type: Task
id: docs-reference-curation:t01
title: Curate the API reference within budgets, gate field docstrings and generate the CLI page
state: completed
priority: P1
verification_strategy: documentation_validation
depends_on: []
files:
  - docs/reference/
  - src/litestar_asyncapi/config.py
  - src/litestar_asyncapi/decorators.py
  - src/litestar_asyncapi/cli.py
  - src/litestar_asyncapi/plugins/core.py
  - src/litestar_asyncapi/plugins/renderers.py
  - src/litestar_asyncapi/asyncapi/datastructures.py
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/spec/
  - tools/docs/scan_public_docstrings.py
  - tools/docs/generate_cli_docs.py
  - tools/docs/postbuild.py
  - tools/docs/verify_docs_artifacts.py
  - zensical.toml
  - Makefile
  - .gitignore
  - .github/workflows/ci.yml
tests:
  - tools/docs/scan_public_docstrings.py
  - tools/docs/verify_docs_artifacts.py
plan_revision: 2
plan_commit: c4349ce
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T19:30:00Z
last_verified_commit: 21723b9
verification_evidence: "make lint 0 (scan-docstrings included), make test 0 (275 passed, 97.01%), make validate-asyncapi 0, make docs 0 (strict 'No issues found', 28 redirect stubs, 57 pages, Reference budgets). Largest page spec/document 95,101 bytes with 14 outline items. Probes: planted undocumented field and 'chapter 3' docstring in a temp fixture exit 1 with both diagnostics; package copy with one field docstring removed exit 1; Reference page padded past 120,000 bytes and a page with 15 outline items exit 1."
created_at: 2026-11-04T19:00:00Z
updated_at: 2026-11-04T19:35:00Z
commit: 21723b9
tags: [docs, reference, docstrings, cli]
---

# Curate the API reference within budgets, gate field docstrings and generate the CLI page

## Objective

The Reference tab lists every public class and function on curated pages, each within 120,000 bytes and 14 outline items; every public dataclass field renders a description; the CLI page is generated from the registered commands; and every previously locked reference URL still resolves.

## Context

- **Why `documentation_validation`.** The deliverables are rendered pages and gates; they are proven by the strict build, the verifier and isolated probes. Source changes are docstrings and option help text only.
- **Invariants.** Master Decisions 6 and 7; Griffe reads source statically, so field descriptions must be inline docstrings; no inline comments; headings without inline code.
- **Canonical surface.** `Makefile::docs`, `Makefile::scan-docstrings`, `tools/docs/verify_docs_artifacts.py::check_reference_budgets`, `tools/docs/postbuild.py::REDIRECTS`.

## Steps

1. Add inline docstrings to every public dataclass field in `config.py`, `decorators.py`, `asyncapi/datastructures.py`, `asyncapi/generator.py` and `spec/**`; replace placeholder class docstrings.
2. Add `tools/docs/scan_public_docstrings.py`, the `scan-docstrings` target in `make lint` and its CI step; prove it on planted violations.
3. Write the curated pages and `tools/docs/generate_cli_docs.py`; redirect the replaced reference URLs; add the budget check and HTML compaction.

## Verification

- **Initial:** `make docs` passes with `reference/core` at 208 KB and `reference/spec` at 332 KB.
- **Final:** `make lint`, `make test`, `make validate-asyncapi` and `make docs` exit `0`; every probe exits `1`.

## Acceptance Criteria

- [x] Each Reference page has 2–5 H2 groups and stays within 120,000 bytes and 14 outline items.
- [x] Every public dataclass field has an inline docstring, enforced by `make lint`.
- [x] The CLI page is generated at build time from `register_commands`.
- [x] Every previously locked reference URL resolves and keeps its fragment.

## Notes & Discoveries

- [2026-11-04 19:05] Former reference URLs: `reference/spec/` is now the section index of the four specification pages. `reference/core/`, `reference/plugins/`, `reference/extractors/` and `reference/schema-generation/` get `index.html` stubs to `plugin/`, `renderers/`, `generator/` and `schema/`; their flat `.html` stubs point straight at the same targets.
- [2026-11-04 19:15] Summary tables and merged `__init__` signatures doubled every field listing; with both on, `spec/document` was 206 KB. `summary = false`, no `merge_init_into_class`, `filters = ["!^_"]`, `show_labels = false` and `show_signature_annotations = true` give typed fields within budget. Constructor arguments of `AsyncAPIPlugin` and `AsyncAPIUIRenderPlugin` moved into their class docstrings.
- [2026-11-04 19:20] `postbuild.py` strips template indentation outside `pre`, `textarea`, `script` and `style` (about 338 KB across the site), which leaves `spec/document` with roughly 25 KB of headroom.
- [2026-11-04 19:20] Dataclass models render all public fields rather than an explicit `members:` list; explicit lists are used where filtering matters (`AsyncAPIPlugin`, `AsyncAPIConfig` ordering, `BaseSchemaObject`, `Schema`).
- [2026-11-04 19:25] Litestar's inventory has no `JsonRenderPlugin` entry, so the renderers page links the Litestar plugins page instead of an autoref.
- [2026-11-04 19:25] CI runs lint as separate jobs, so the scanner also runs as a step in the `prek` job.
