# Change Log

Date-grouped record of Flow lifecycle events, migrations, and completed work.

## 2026-11-05

### Completed: `contract-ergonomics`
- Document metadata and security scheme definitions are inherited from `app.openapi_config` through `asyncapi/openapi.py`; the default title is now the OpenAPI title (breaking). Requirements and tags are not inherited.
- `inherit_openapi_servers=True` derives `ws`/`wss` servers from absolute OpenAPI URLs, bound only to WebSocket channels.
- Security schemes, servers and replies (`ReplyDefinition`) are referenced by name; the contract example is split into a Learn request/reply and a JWTAuth security example; schema-name parity with Litestar OpenAPI is pinned.
- The `jwt` extra joined the `tests` dependency group; `openapi-3.0.0`/`openapi-3.1.0` fixtures cover every mapped scheme type and derived servers.

## 2026-11-04

### Completed: contract fixes, realtime discovery, docs migration
- `contract-fixes` completed: leaked environment details removed, lint green, wire keys and Draft07 export corrected, payload schema fidelity, listener naming, decorator merging, single-plugin and root-path guards, console unions, and test/gate debloat (coverage now measures handler threads).
- `realtime-discovery` completed (issue #11): `x-litestar-source` transport markers and bindings, Server-Sent Event discovery, ChannelsPlugin topics with `channel_payloads`; runtime-subscribed topics are never published.
- `docs-redesign` completed: Zensical site with Learn, Integrations, Reference and Project tabs, executed examples, budgeted Reference pages, generated CLI page and redirects from the Sphinx URLs.
- Also: frontend builds on Node 26 from `.nvmrc`; the package imports without pydantic; Python support is 3.11–3.15.

### Planning: audit and three approved PRDs
- Audited the tree at `23d1a4a` across generation, schema, docs UI and AsyncAPI 3.0/3.1 conformance; promoted the findings into `specs/contract-fixes/research/codebase-audit_20261104.md`.
- Approved `docs-redesign` (Zensical migration, four tabs, executed examples), `contract-fixes` (verified bugs, leak removal, debloat ledger) and `realtime-discovery` (issue #11: transport markers, SSE discovery, typed ChannelsPlugin topics). Each passed one independent review round with all findings adopted.
- Pointed project URLs and the Codecov slug at `cofin/litestar-asyncapi`; closed four superseded Dependabot PRs.

### Setup alignment (`synthesize` / `verify` at 49bc3c8)
- Verified knowledge against the current tree and corrected drift: Litestar bound is `>=2.24.0` with no cap; application-encoder normalization lives in `AsyncAPIPlugin` and `normalize_examples`; JSON Pointer tokens are also percent-encoded; removed the unused `litestar.utils.predicates` pattern.
- Added `product/index.md`, `domains/asyncapi-contracts.md`, `testing/{public-seam-tdd,distribution-and-browser}.md`, `gotchas/runtime-and-tooling.md`, and split decisions into ADR-001..003.
- Split `patterns/testing-and-security.md` into `patterns/renderer-security.md`, `patterns/ci-supply-chain.md` and the testing chapters.
- Recorded the focused-test `--no-cov` requirement and the `no_future_annotations` hook.
- Synced `knowledge/workflow.md` to the current Flow template; removed the retired transaction-journal protocol.
- Generated project skills and paired subagents for asyncapi-generation, asyncapi-schema, asyncapi-docs-ui and asyncapi-release-ci.
- Removed legacy `skills/flow-memory-keeper/`, `transactions/` and `.agents/index.md`; switched `.agents/` to shared tracking.

## 2026-09-21

### Flow Archive: AsyncAPI September 2026 redesign (`asyncapi-redesign-20260920`)

Archived flow `asyncapi-redesign-20260920` after 16 closed tasks and final release preparation (range `228ad94..15bc460`). Durable knowledge contracted into `knowledge/architecture/` (04-schema-generation, 06-render-plugins-and-ui), `knowledge/patterns/plugin-architecture.md`, and `knowledge/workflow.md`. Spec directory deleted under `local-only` stealth mode policy.

## 2026-09-20


### Flow: AsyncAPI September 2026 redesign (`asyncapi-redesign-20260920`)

Completed 16 tasks on the existing branch, range `228ad942818159c19609a43f59d796816a74bbeb..68e46f5fd61f83fbf3426f7b3fbb9c82dd9d292d` (including native serialization inlining). Reused native Litestar schema/DTO/serialization/rendering/routing/CLI components, consolidated plugins, removed obsolete shims and custom playground, corrected Draft07 wire contracts and deterministic assembly, and packaged upstream documentation/interaction. AsyncAPI React is default; Scalar remains opt-in after fidelity failures. The user approved clean API breaks and advisory validation with intentional invalid sends.

Verification:212source tests93.34%, five installed Python3.10–3.14 lanes212each, latest2.24.0 lane,10JS,19source/19installed browser, official validation, lint, wheel/sdist/licenses and docs gates pass. Ten examples and README execute with real frames/routes/exports. Both final correctness and independent quality reviews have no findings. Migration is in `docs/migration.rst`; durable decisions are in `knowledge/decisions/asyncapi-redesign-20260920.md`. Flow revision9/state44 is completed; the plan is retained locally, not archived. No hosted writes or CI execution were performed.

### Flow: Modernize Project Tooling, CI, and Configuration (`modernize-project-tooling`)
- Migrated hook execution from `pre-commit` to `uvx prek` with standardized `tools/hooks/no_future_annotations.py`.
- Modernized packaging and dependencies in `pyproject.toml`: Python 3.14 classifier, updated dependency groups, `[tool.ruff.format]`, `[tool.ruff.lint.per-file-ignores]`, `[tool.pyright]` configuration, and fixed 9 typing discrepancies.
- Modernized `Makefile` with `.SHELLFLAGS := -euo pipefail -c`, `prek`, `zizmor`, `WORKING_TREE_FILES`, `docs-audit`, `release`, and `check-all`.
- Hardened all GitHub Actions workflows (`ci.yml`, `test.yml`, `docs.yml`, `pr-title.yml`, `publish.yml`): full commit SHA pins, `persist-credentials: false`, `permissions: contents: read`, `pull_request` trigger, disabled uv cache on publish, and `$/` self-repository syntax.
- Configured `.vscode/settings.json` and `.vscode/launch.json` adhering to modern workspace standards.
- Rebuilt Sphinx documentation architecture: modernized `conf.py` (pruned 18 unused extensions), created `tools/docs_audit.py`, overhauled all guides across `docs/usage/`, created examples gallery indexing all 6 runnable PEP 723 applications, modularized `docs/reference/`, and verified clean build under `make docs`, `make docs-audit`, `make docs-linkcheck`.
- Executed full aggregate quality gate (`make check-all`): prek, mypy (50 files), pyright (0 errors), slotscheck (50 modules, 63 classes), zizmor (0 findings), validate-examples, validate-pep723, test-all (142 passed, 91.70% coverage), and package build.

### Flow Setup & OKF v0.2 Alignment
- Initialized hierarchical Open Knowledge Format (OKF v0.2) bundle layout under `.agents/bundles/`.
- Scaffolding materialized:
  - Root bundle index: `bundles/index.md` (`okf_version: "0.2"`).
  - Product bundle: `bundles/product/product.md`, `bundles/product/tech-stack.md`, `bundles/product/product-guidelines.md`.
  - Knowledge bundle: `bundles/knowledge/workflow.md`, `bundles/knowledge/architecture/overview.md`.
  - Pattern chapters: `bundles/knowledge/patterns/plugin-architecture.md`, `bundles/knowledge/patterns/schema-generation.md`, `bundles/knowledge/patterns/testing-and-security.md`.
  - Style guide chapters: `bundles/knowledge/styleguides/python.md`, `bundles/knowledge/styleguides/bash.md`.
  - Registries: `bundles/specs/index.md`, `bundles/research/index.md`.
- Workflow chapter rewritten to latest OKF v0.2 standard with canonical repository Makefile commands and direct-read continuity.
- Historical data from past completed flows (`litestar-asyncapi-9jd`, `litestar-asyncapi-0el`, `litestar-asyncapi-t5i`) synthesized and elevated into knowledge base.

## 2026-04-20

### Flow: v1 Release Readiness (`litestar-asyncapi-t5i`)
- Implemented `AsyncAPIPlaygroundRenderPlugin` providing a turnkey browser-based WebSocket testing UI at `/playground`.
- Added dynamic channel selector, live connection indicators, message composer with JSON syntax checking, and filterable message logs.
- Added runnable reference examples under `docs/examples/` with PEP 723 script blocks and CI validation scripts (`validate_doc_markers.py`, `validate_pep723_blocks.py`).
- Initialized Sphinx documentation with Shibuya theme and customized syntax highlighting.

### Flow: Project Alignment & Infrastructure (`litestar-asyncapi-0el`)
- Modernized repository tooling and configuration to align with `litestar-mcp` standards.
- Added runtime package metadata support in `src/litestar_asyncapi/__metadata__.py`.
- Modernized Makefile targets for `make install`, `make test`, `make lint`, `make coverage`, and `make check-all`.

## 2026-04-19

### Flow: Quality Audit & Hardening (`litestar-asyncapi-9jd`)
- Aligned WebSocket route discovery with Litestar upstream patterns (`include_in_schema` checking).
- Implemented AsyncAPI 3.0 fixed-length tuple mapping using `prefixItems` (JSON Schema Draft 2020-12).
- Simplified `Parameter` object generation to adhere to AsyncAPI 3.0 specification (stripped inner schema).
- Implemented case-insensitive `operationId` collision detection using `.casefold()` and added `strict_uniqueness` config flag.
- Integrated canonical Litestar utilities (`litestar.utils.predicates`, `litestar.utils.typing`).
- Secured UI renderers against XSS via server-side `html.escape` and client-side `escapeHtml`.
- Reached >92% test coverage across all core `asyncapi/` modules.
- Verified deep nested router discovery in integration tests.
