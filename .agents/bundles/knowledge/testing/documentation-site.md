---
type: Guide
title: Documentation Site Verification
description: Executed examples, curated reference output and legacy URL acceptance.
tags: [asyncapi, contracts]
status: stable
generated:
  by: flow-completion
  at: 2026-11-04
verified:
  - by: flow-completion
    at: 2026-11-04
    commit: dcc21c01b0e1e0bad5f4547dad61f075364629c2
sources:
  - id: export
    resource: tools/docs/export_example_documents.py
    title: Executed document exports
  - id: reference
    resource: tools/docs/scan_public_docstrings.py
    title: Public field documentation
  - id: redirect
    resource: tools/docs/postbuild.py
    title: Legacy API fragments and whitespace compaction
  - id: verify
    resource: tools/docs/verify_docs_artifacts.py
    title: Built site acceptance
---

# Documentation Site Verification

<!-- truth: start -->
- make docs regenerates CLI reference and all example document fragments before strict Zensical build.
- Source tests serve every runnable example; official AsyncAPI validation checks its exported document.
- Generated docs/_generated and docs/reference/cli.md are ignored artifacts.
- Reference pages stay within 120000 bytes and 14 outline items.
- Legacy API links need both the destination page and its renamed public API anchor.
<!-- truth: end -->

## Example and reference acceptance

Each runnable example declares PEP 723 metadata and a module-level Litestar app. Source pytest serves its schema endpoint, while export_example_documents builds canonical JSON and snippets used by documentation.[^export] Installed tests skip these source-only examples, so source execution, installed package acceptance and official validator results are separate evidence.

Public dataclass fields need inline docstrings checked by the AST scanner.[^reference] Curated mkdocstrings member lists must include newly added configuration fields. Avoid duplicate field listings so pages remain within the size and outline budgets.

## Redirects and artifacts

postbuild compacts whitespace outside pre, textarea, script and style, then creates former flat and renamed-directory redirects.[^redirect] API fragment maps derive implementation-module aliases from actual rendered public anchors and route split spec models to their current pages. Missing method anchors fall back to an existing enclosing class anchor. Ordinary heading fragments remain unchanged. The artifact gate validates inventory, redirect maps, local links, anchors and reference budgets.[^verify]

make docs-linkcheck requires lychee; a reported skip is not external-link validation. Hosted docs success proves only the checked revision's links.

[^export]: `tools/docs/export_example_documents.py`
[^reference]: `tools/docs/scan_public_docstrings.py`
[^redirect]: `tools/docs/postbuild.py`
[^verify]: `tools/docs/verify_docs_artifacts.py`
