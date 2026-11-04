---
type: Spec
flow_id: contract-fixes
title: Contract Fixes and Debloat
description: Fix the verified wire-contract, discovery and docs-routing bugs from the 2026-11-04 audit, remove leaked internal environment details, and cut test and gate bloat without weakening verification.
state: planned
parent_prd: null
research: [research/codebase-audit_20261104.md]
plan_revision: 2
plan_commit: 23d1a4a
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [prd, bugs, conformance, debloat, hygiene]
---

# Contract Fixes and Debloat

## 1. North Star Goal & Context

### Objectives

Every document the plugin emits says what the application actually does, and validates where the official AsyncAPI tooling would check it. The repository contains nothing private, and its tests and gates are small enough to trust and fast enough to run on every change.

### Current State & Limits

- **Green suite, wrong output.** 212 tests pass at 93% coverage, but the audit ([`research/codebase-audit_20261104.md`](research/codebase-audit_20261104.md)) reproduced six bugs that emit a wrong contract or a wrong docs page. Examples:
  - Kafka binding keys are wrong.
  - Every listener operation is named `ListenerHandler_*`.
  - Two plugins cross-link their docs.
  - Item types are lost on constrained variadic tuples.
  - Zero bounds are dropped.
  - `prefixItems` leaks into Draft07 documents.
- **Validator blind spot.** `tools/validate_asyncapi.mjs` validates hand-written fixtures. They include security schemes, traits and `ws` bindings, but no Kafka or AMQP bindings and no `x-` extensions. That is why the Kafka key bug passed.
- **Private details in a public repo.** `Makefile` (an OS-detection block plus `setup-env` help text) and `tools/scripts/setup-env.sh` name an internal environment. The index URLs they set are public PyPI. Both files are already on `origin/main`.
- **Lint is red.** codespell flags the pytest key `addopts`. `pyproject.toml::tool.pydantic-mypy` sets the option `warn_untyped_fields`, which pydantic-mypy does not recognize.
- **Bloat:**
  - Some code exists only to serve synthetic tests: the merge path in `_normalize_channels` is reached only by monkeypatched extractor output.
  - Six attribute probes guess at Litestar handler internals.
  - 41 test files carry `anyio` markers, but there are no async tests.
  - Some constructor tests just echo their inputs.
  - slotscheck runs as both a hook and a target.
  - `make check-all` runs the suite twice.

### What Is New & Why It Succeeds

- **One chapter per domain.** Fixes are grouped by the domain skill that owns them (`asyncapi-generation`, `asyncapi-schema`, `asyncapi-docs-ui`, `asyncapi-release-ci`), and each chapter has one reviewer. Where chapters share files, the merge order in Section 3 applies.
- **Fixture first.** A conformance fixture covering bindings, security, traits and extensions joins the official validation gate before the wire fixes land, so the class of bug that let B1 through stays caught.
- **Listener unwrapping in one place.** `_compat.py::websocket_handler_name` already unwraps listeners, but only for provenance. It is split into a callback helper and a name helper that returns `__name__`. Operation naming and docstring lookup then use them too, which fixes B2 and removes the six attribute probes together.
- **Proven gates before deletions.** Every deleted test or gate is first replaced by a proven equal-or-stronger check, following the `flow:debloat` rules.

### Impact

- **Users** get correct operation names, correct binding keys, and payload schemas that keep their constraints.
- **Maintainers** get a green `make lint`, one way to run each gate, and fewer tests to read.

### Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| The B2 fix renames operation and message keys that users may have pinned. | Pre-1.0 Alpha (`0.2.0`). Record it as a breaking change under Fixed in `docs/changelog.rst`, and update `src/tests/integration/test_cli.py`. |
| Removing code reached only by synthetic tests could remove a real path. | Chapter 4 first adds an assertion over the whole integration suite that no two discovered channels share a key, and deletes code only while it holds. |
| A replacement gate could be vacuous. | Each replacement is proven against a planted violation in an isolated fixture before the old gate is deleted, as `flow:debloat` requires. |
| Removing the internal index setup breaks the author's local install. | Keep it in a git-ignored local override, `uv.toml` or `Makefile.local`, loaded with `-include`. |

### Success Metrics

- `make lint`, `make type-check`, `make test` and `make validate-asyncapi` pass. The new conformance fixture is part of `make validate-asyncapi`.
- Every bug B1–B12 in the audit has a public-seam regression test that fails before its fix. B13 is verified first.
- `git grep -i` for the internal environment name returns nothing. The public PyPI URLs are not part of this check.
- Test count drops while line and branch coverage of `src/litestar_asyncapi` stays at or above the baseline of 93.35%.

## 2. Locked Architectural Decisions

1. **Leak removal: from the tree only.** User decision. History is not rewritten. Internal index configuration moves to a git-ignored local file.
   - Rejected: rewriting history (breaks clones and tags).
   - Rejected: rotating URLs (not a credential).
2. **Allow only one `AsyncAPIPlugin` per app.** `AsyncAPIPlugin.on_app_init` raises `ImproperlyConfiguredException` when `app_config.plugins` holds another `AsyncAPIPlugin` instance (`plugin is not self`). It raises whether or not docs are enabled, so the first plugin to initialize reports the conflict. This mirrors Litestar, which has one `openapi_config` per app, registers one internal `OpenAPIPlugin`, and uses fixed route names (`litestar.openapi.controller`). Several docs sites per app is backlog.
   - Rejected: per-plugin scoped route names. Litestar does not support this, so the user deferred it.
3. **`Schema.prefix_items` is converted on export.** User decision. The public field stays.
   - Only the `prefixItems` rule moves out of `asyncapi/schema_generation/dialect.py`, into a small shared helper. Calling all of `to_asyncapi_schema` would create an import cycle and also rewrite `$defs`/`$ref`.
   - `to_schema` emits `items: [..prefix..]`. If `items` is also set, it becomes `additionalItems`. Setting both `items` and `additional_items` alongside `prefix_items` raises `ValueError`.
   - Rejected: removing the field (a public API break).
4. **Key normalization becomes explicit.** `spec/base.py::_normalize_key` keeps camelCase as the default and uses `metadata["alias"]` whenever it is present. The implicit `schema_` and `_in` rules are deleted.
   - Every `Schema` keyword and `SecurityScheme.in_` already declares an alias. The only wire change is that the five Kafka `schema_*` fields become correct.
   - `_compat.py::normalize_native_schema` is a second caller and gets its own regression test.
   - Rejected: special-casing the Kafka fields, which leaves the latent `_in` hazard.
5. **One listener-unwrapping helper.** Split `_compat.py::websocket_handler_name`, which today unwraps `ListenerHandler._fn` and returns `__qualname__`, into two functions:
   - `websocket_handler_callback`, which returns the user callback;
   - `websocket_handler_name`, which returns its `__name__`. Using `__name__` keeps `<locals>` out of component keys.

   Operation ids (`extractors/websocket.py::_infer_operations_from_handler`), docstrings (`asyncapi/utils/docstrings.py`) and the existing WebSocket provenance use them. ChannelsPlugin provenance is out of scope, because those handlers are not listeners. Private Litestar access stays confined to `_compat.py`.
6. **Decorator metadata order.** Decorator overrides apply first. The fill-if-empty pass for handler `opt` metadata and docstrings runs last, so an explicit decorator `operation_id` still wins.
7. **Decorator merging.** `asyncapi_operation(messages=...)` and `asyncapi_message` merge by message name in either stacking order, raise on conflicting names, and re-run `OperationDefinition` validation after the merge.
8. **Validation in `__post_init__`.** `DocsConfig.path` rejects `"/"`. `AsyncAPIConfig.spec_version` is checked against `{"3.0.0", "3.1.0"}`. `OperationDefinition.action` normalizes with `.strip().lower()`, and `decorators.py::_coerce_action` is deleted.
9. **Debloat ledger.** The ledger in Section 6 is binding. Items marked *keep* are not to be "cleaned up" by any chapter.

## 3. Master Roadmap (Ordered Child Flows)

| Chapter | Flow ID | Title | Key Deliverables | Public Seams | Dependencies | State |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `public-hygiene` | Remove leaked internals, green lint | Leak removal and local override, codespell and mypy config fixes, planning-label comment removed | `make install`, `make lint` | none | completed |
| 2 | `wire-contract-fixes` | Wire keys and conformance fixture | B1, B6, alias-only normalization, bindings/security/traits/extensions fixture in official validation | `BaseSchemaObject.to_schema`, `make validate-asyncapi` | 1 | completed |
| 3 | `schema-fixes` | Payload schema fidelity | B4, B5, B9, B10, B11, schema error message cleanup | `AsyncAPISchemaGenerator`, generated `components/schemas` | 1 | completed |
| 4 | `discovery-fixes` | Discovery, naming and decorators | B2, B7, B8, B12 (action, spec_version), listener-unwrapping helper, discovery debloat ledger items | `AsyncAPIGenerator.build_schema`, `asyncapi_operation`, `asyncapi_message` | 1 | completed |
| 5 | `docs-routing-fixes` | Docs routing and console | B3 single-plugin guard, B12 `path="/"`, B13 console unions (verify first), manifest caching | `AsyncAPIPlugin`, `DocsConfig`, docs routes | 1 | completed |
| 6 | `test-gate-debloat` | Test and gate debloat | anyio markers, echo tests, duplicate slotscheck, `check-all` double run, Makefile aliases, ruff ignores, future-annotations hook → ruff (if proven), `.agents` command duplication | `make lint`, `make check-all` | 2, 3, 4, 5 | draft |

**Merge order:** 1 → 2 → 3 → 4 → 5 → 6. The chapters share these files:

| File | Chapters |
| --- | --- |
| `spec/base.py::_normalize_key` | 2, 3 (`normalize_native_schema` caller) |
| `_compat.py`, `asyncapi/generator.py` | 3, 4 |
| `config.py` | 4, 5 |
| `Makefile`, `tools/validate_asyncapi.mjs` | 1, 2, 6, and `docs-redesign` |

Chapter 6 runs last so it does not churn test files that chapters 2–5 rewrite.

## 4. Global Constraints (Applicable to All Child Flows)

- **Fix workflow.** Each fix starts with a failing public-seam test in the existing canonical test file for that module (`behavior_tdd`). Debloat deletions use a green-before / green-after characterization baseline, and coverage of `src/litestar_asyncapi` must not drop.
- **Skills.** Load the domain engineering skill before changing code, and its `review-*` skill for the chapter review.
- **Project conventions:** no inline comments, no `from __future__ import annotations` in package code, slotted classes, private Litestar imports only in `_compat.py`, and Draft07 wire output.
- **Breaking output changes** are listed under Fixed in the changelog in plain language. Two are known: listener operation keys, and Kafka binding keys.
- **Cross-PRD rule with `docs-redesign`:**
  - Write to whichever changelog or contributing file exists at merge time (`.rst` before the docs migration, `.md` after).
  - Field docstrings added to `spec/**`, `config.py` and `datastructures.py` must follow that PRD's inline-docstring rule, so its chapter 3 does not redo them.
- **Out of scope:** the docs-site migration (`../docs-redesign/spec.md`) owns `tools/docs_audit.py`, `tools/sphinx_ext/`, `tools/ci/validate_doc_markers.py` and the `docs-audit`/`validate-examples` targets. This PRD does not touch them.
- **Public text** (commits, PRs, changelog) carries no internal names, planning labels or ceremony.

## 5. Backlog (Deferred Items)

- Multiple `AsyncAPIPlugin` instances per app, with scoped route names. Litestar's OpenAPI has no equivalent.
- AsyncAPI feature gaps from the audit:
  - Info metadata, the document `id` and root extensions in `AsyncAPIConfig`.
  - Typed `OAuthFlows`/`OAuthFlow` models.
  - Mapping Litestar auth backends and guards to security schemes.
  - WebSocket channel bindings from route parameters.
  - Kafka/AMQP/HTTP operation bindings.
  - Avro and other multi-format schema helpers.
- Inherited from Litestar: a field default written onto a shared enum component schema. Report it upstream instead of patching locally.
- Serving cached JSON bytes directly from the docs route (see the ledger).

## 6. Debloat Ledger

Each candidate is classified by tracing its callers, re-exports, `opt` strings and tests, with coverage measured with per-test contexts.

| Candidate | Class | Verdict | Evidence and condition |
| --- | --- | --- | --- |
| `generator.py::_normalize_channels` same-identity merge block, and the per-channel operation dedupe loop that follows it | private-dead in production | delete both (ch 4) | Reached only by three `test_generator.py` tests: `test_same_route_merge_is_stable_and_selects_only_its_messages`, `test_shared_named_message_constraints_cannot_be_deduplicated` and `test_conflicting_discovered_channels_do_not_overwrite`. All three monkeypatch `extract_websocket_channels` with channels that share a route identity, which neither extractor can produce. Keep the duplicate-key raise. Rewrite the conflict test through real routes and delete the other two. |
| `generator.py::_populate_operations` `Reference` guard | private-dead, type-narrowing | replace (ch 4) | Uncovered, because channels are always built inline. It narrows the type for mypy, so replace it with a type-safe lookup (a typed inline-channel map) rather than deleting it. |
| `extract_websocket_channels(config=None)` default | public | keep | Exported from `asyncapi/extractors/__init__.py` and documented in `docs/reference/extractors.rst`. |
| `_path_parameters_to_parameters(schema_generator=)` | private-live (two callers) | drop the argument (ch 4) | The argument is unused. Callers are `extractors/websocket.py` and `extractors/channels.py`. |
| `_is_none_return_type`, `_should_include_handler` | private-live | simplify (ch 4) | Overlapping predicates, and an always-true `hasattr(handler, "opt")`. Characterize first. |
| `asyncapi/utils/docstrings.py::_iter_docstring_candidates` | private-live | replace with the Decision 5 helper (ch 4) | Six speculative attribute probes and one caller. |
| `unit/extractors/test_websocket_helpers.py` | test-only, private | delete after behavioral replacement (ch 4) | Calls private `_infer_content_type` and `_is_none_return_type` directly. Replace with public-seam cases covering Reference, array and untyped payloads. |
| `unit/test_decorators_storage.py` | test-only | merge into `test_decorators.py` (ch 4) | A single test. Chapter 4 rewrites decorator merging anyway. |
| `unit/extractors/test_websocket_discovery_alignment.py`, `test_operation_id_hardening.py` | test-only | merge into `integration/test_discovery.py` and rename (ch 4) | Single-purpose file and a remediation-style name. |
| `plugins/core.py` per-request `deepcopy` | public safety | keep | `DocsConfig` accepts user render plugins. The copy keeps them from mutating the cache. |
| `plugins/core.py::_cached_json` | public-live | keep | Backs `AsyncAPIPlugin.get_asyncapi_json`, used by `cli.py` and `integration/test_plugin_cache.py`. |
| `deepcopy` in `_get_document` | private safety | keep when caching; skip only when `use_cache=False` (ch 5) | `generator.py` shares the config's `Server` objects with the document, so the copy protects the cache. Without caching, the outer getter's copy already isolates the caller. |
| `docs.py::bootstrap_html` manifest re-read | private | cache the parsed manifest (ch 5) | Keep the `OSError`/`KeyError`/`ValueError` fallback. |
| `pytest.mark.anyio` in 40 test files plus `conftest.py::anyio_backend`; the `anyio` test dependency | test-only | delete, and drop the dependency unless something else imports it (ch 6) | There are zero `async def test` functions. |
| `src/tests/test_plugin.py` tests 1–4 and their fixtures | test-only | delete the echo tests (ch 6) | Move the `title`/`version`/`description`/`servers` default assertions from `test_config_defaults` into `unit/test_config.py::test_config_defaults`, which does not cover them, and move `test_nested_docs_route_configuration` to `integration/test_routes.py`. |
| slotscheck as a prek hook, a `make` target and a CI job | gate | keep `make slotscheck` and the CI job; drop the prek hook (ch 6) | Prove that a planted unslotted class fails `make slotscheck`. |
| `check-all` running `test-all` and `coverage`; the `test-all`/`pre-commit` aliases; the identical `mypy`/`mypy-nocache` targets | gate | dedupe (ch 6) | The suite currently runs twice. |
| `tools/hooks/no_future_annotations.py` | gate | replace with ruff `banned-api` only if proven, else keep and add a self-test (ch 6) | |
| Test `per-file-ignores` `S101` alongside `S`, blanket `PT` | gate | narrow (ch 6) | `ruff check` stays clean. |
| `.agents/**` command lists repeated 4–7 times | prose | point to `knowledge/workflow.md` (ch 6) | |

## Implementation Plan

- [x] public-hygiene — remove leaked internals, green lint (../public-hygiene/spec.md)
- [x] wire-contract-fixes — key normalization, prefixItems export, conformance fixture (../wire-contract-fixes/spec.md)
- [x] schema-fixes — tuple, bounds, example and null fidelity (../schema-fixes/spec.md)
- [x] discovery-fixes — listener naming, metadata order, decorator merging, discovery debloat (../discovery-fixes/spec.md)
- [x] docs-routing-fixes — single-plugin guard, root path, console unions, caching (../docs-routing-fixes/spec.md)
- [ ] test-gate-debloat — tests and gates trimmed with proven replacements (../test-gate-debloat/spec.md)

## Continuity Snapshot

- **State:** planned. Chapters 1–5 (`public-hygiene`, `wire-contract-fixes`, `schema-fixes`, `discovery-fixes`, `docs-routing-fixes`) are completed; `test-gate-debloat` is next.
- **Review:** round 1 of the independent review is adjudicated. All 16 findings were adopted, and `plan_revision` is now 2.
- **Discoveries:**
  - `coverage.xml` in the working tree can be stale after partial runs. Regenerate it before comparing coverage.
  - Issue #11 (`../realtime-discovery/spec.md`) builds on chapter 4's extractors and lands after it.
  - Coverage omits the `thread` concurrency, so docs request-handler code is never traced. Chapter 6 should decide whether to add it.
