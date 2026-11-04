---
type: Task
id: docs-learn-content:t01
title: Rewrite the Learn and Integrations guides around executed examples and generated output
state: completed
priority: P1
verification_strategy: documentation_validation
depends_on: []
files:
  - docs/learn/
  - docs/integrations/
  - docs/examples/server_sent_events.py
  - docs/examples/transports.py
  - docs/examples/payload_schemas.py
  - docs/examples/channels_plugin/app.py
  - docs/project/migration.md
  - docs/project/contribution-guide.md
  - docs/index.md
  - tools/docs/export_example_documents.py
  - zensical.toml
  - Makefile
tests:
  - src/tests/unit/docs/test_examples.py
  - tools/docs/verify_docs_artifacts.py
plan_revision: 2
plan_commit: 6ccfaa7
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T20:00:00Z
last_verified_commit: 3afc896
verification_evidence: "make lint 0, make test 0 (278 passed, 97.01%), make validate-asyncapi 0 (13 example documents), make docs 0 (export before build, strict 'No issues found', 28 redirect stubs, 58 pages, Reference budgets). make docs-linkcheck printed its skip message (lychee not installed). Former section anchors (server-sent-events, tuple-and-schema-dialect, examples, opt-in-websocket-console, explicit-broker-traits-and-replies, guarded-mounted-documentation, headless-export, gallery ids) present in the built pages."
created_at: 2026-11-04T19:40:00Z
updated_at: 2026-11-04T20:00:00Z
commit: 3afc896
tags: [docs, content, examples]
---

# Rewrite the Learn and Integrations guides around executed examples and generated output

## Objective

Every Learn guide opens with a tested example from `docs/examples/`, shows the document section it produces from `docs/_generated/`, explains it in a short walkthrough and ends with a three-bullet recap that links onward; the Integrations guides follow the same example-first shape at their locked URLs.

## Context

- **Why `documentation_validation`.** Content and build wiring change; proven by the strict build with snippet path checks, the example tests and the official schema gate.
- **Invariants.** Locked URLs from `docs-zensical-foundation`; output is never hand-written; examples keep PEP 723 blocks, a module-level `app` and no inline comments; headings are unnumbered and free of inline code.
- **Canonical surface.** `docs/learn/*.md`, `docs/integrations/*.md`, `tools/docs/export_example_documents.py::fragments`, `Makefile::docs`.

## Steps

1. Add the Server-Sent Event, payload-schema and discovery-source examples; type the `news` topic in the ChannelsPlugin example.
2. Write each top-level section and each non-empty `components` map as a fragment file and run the export in `make docs` and `make docs-serve`.
3. Rewrite the Learn and Integrations pages in place, add the export guide, fix the migration note on Server-Sent Events and the contributor Node note.

## Verification

- **Initial:** `make docs` passes; Learn pages carry no generated output.
- **Final:** `make lint`, `make test`, `make validate-asyncapi` and `make docs` exit `0`.

## Acceptance Criteria

- [x] Every Learn guide opens with an executed example and shows generated output.
- [x] Pages stay within about 200 lines with unnumbered headings without inline code.
- [x] Server-Sent Event discovery, `channel_payloads`, topic-only channels, `x-litestar-source` and bindings, the one-plugin rule, the Pydantic note for generated examples and the `.nvmrc` note are covered.
- [x] Former section anchors keep resolving.

## Notes & Discoveries

- [2026-11-04 19:45] `docs/_generated/` is ignored by Git, so `make docs` runs the export in `.venv-docs` before the build; the docs environment imports every example without the test extras.
- [2026-11-04 19:50] The CLI writes compact JSON, so pages show indented fragments of the same canonical document instead of terminal output.
- [2026-11-04 19:50] Exporting with the CLI got a new Learn page at `learn/export/`; no locked URL moved. The mounting guide stays on the security page to keep its former anchors.
- [2026-11-04 19:55] On Litestar 2.25 automatic examples work without Pydantic; the guide states the dependency conditionally, since the package documents that Litestar's example factory can require it.
- [2026-11-04 19:55] lychee is not installed locally; external links remain checked only in CI.
