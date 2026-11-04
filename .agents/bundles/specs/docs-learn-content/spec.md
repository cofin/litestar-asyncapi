---
type: Spec
flow_id: docs-learn-content
title: Learn and Integrations Rewrite
description: Rewrite the Learn and Integrations guides as example-first Markdown pages at locked URLs.
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
tags: [docs, content, information-architecture]
---

# Learn and Integrations Rewrite

## Charter

Rewrite the converted Learn and Integrations guides as short, task-focused pages. Each Learn page follows four parts:

1. A runnable example from `docs/examples/**`, included with snippets.
2. The exact document fragment or terminal output it produces.
3. A 3–5 paragraph walkthrough.
4. A 3-bullet recap that links to the next page.

## Upstream Dependencies

- `docs-examples-verified`: the examples shown must already run in tests.
- `docs-zensical-foundation`: the tabs, snippets and styling.
- `docs-reference-curation`: the reference anchors that the pages link to.

## Key Deliverables

- **Learn:**
  - Installation and setup, merging the current getting-started and quickstart pages, with synchronized `uv`/`pip`/`pdm`/`poetry` tabs.
  - Core concepts.
  - WebSocket handlers: listeners, streams and raw sockets.
  - Explicit contracts and decorators.
  - Schema generation, covering the Draft07 dialect, tuple bounds and examples.
  - Exporting documents with the CLI.
  - An examples gallery.
- **Integrations:**
  - ChannelsPlugin.
  - The documentation UI and renderers, covering React and Scalar, the optional console and its advisory validation limits.
  - Security and servers.
  - Mounting and guarding docs under a router.
- **Output fragments.** Pages show document fragments by snippet-including the files in `docs/_generated/`, which chapter 1's export tool writes. They are never typed by hand.
- **Rewrites happen in place**, at the page URLs locked in chapter 2. The Project pages are already converted in full there and are out of scope here.
- **Page size.** Each page is at most about 200 lines, with no inline code or numbering in headings.

## Public Seams

- `docs/**/*.md`
- `docs/examples/**`

## Acceptance Boundary

`make docs` passes with snippet path checks on, every Learn page opens with an executed example, and `make docs-linkcheck` reports no broken internal or external links.
