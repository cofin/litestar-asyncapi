---
type: Guide
title: Project Workflow
description: Canonical build, lint, typecheck, test, and Flow execution rules for litestar-asyncapi.
tags: [workflow, commands, verification]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: make
    resource: Makefile
    title: Canonical targets
  - id: addopts
    resource: pyproject.toml::tool.pytest.ini_options
    title: Pytest and coverage configuration
  - id: ci
    resource: .github/workflows/ci.yml
    title: CI gate composition
---

# Project Workflow

<!-- truth: start -->
- Task worksheets under `.agents/bundles/specs/<flow_id>/tasks/<id>-<slug>.md` and `spec.md` checklists are the sole authority for task state and commits.
- Setup `make install`; focused test `uv run pytest <path> -q --no-cov`; lint + types `make lint`; aggregate gate `make check-all`.
- Focused runs need `--no-cov`: the global `--cov-fail-under=80` addopt makes any partial run exit 1.
- Frontend or packaging changes also run `make js-install build validate-asyncapi js-test browser-test` (Node (`.nvmrc`)).
- Every task worksheet declares one `verification_strategy` (`behavior_tdd`, `regression_tdd`, `characterization`, `static_validation`, `documentation_validation`, `integration_acceptance`).
- Test through confirmed public seams in existing canonical module test files; never mock the System Under Test, write tautological assertions, or create standalone `test_*remediation*.py` / `test_*audit*.py` files.
- Project-local domain and review skills live under `.agents/skills/` and paired subagents under `.agents/agents/`.
- Never create or mutate Git tags, and never push or open PRs without explicit user instruction.
<!-- truth: end -->

## Canonical Commands

This is the single command reference for the repository; other `.agents` files and `AGENTS.md` point here. Prefer `Makefile` targets[^make]; run Python tools through `uv run`.

```bash
# setup
make install                                   # uv sync --all-extras --dev
make js-install                                # npm ci (Node (`.nvmrc`); build/test only)

# focused test (red-capable)
uv run pytest src/tests/unit/test_generator.py::test_name -q --no-cov

# lint & typecheck
make lint                                      # prek, type-check, slotscheck, zizmor, validate-pep723
make prek                                      # ruff (incl. the future-annotations ban), codespell, file hygiene on tracked and untracked files
make type-check                                # mypy and pyright
make slotscheck                                # every class defines __slots__ unless excluded in pyproject.toml
make zizmor                                    # workflow security scan
make validate-pep723                           # PEP 723 metadata in docs/examples
make fix                                       # ruff autofix + format

# tests
make test                                      # full suite once, coverage floor 80
make coverage                                  # same suite under xdist, plus HTML and XML reports
make check-all                                 # lint, then the suite once

# packaged frontend and installed distribution
make build                                     # Vite assets, wheel and sdist, asset completeness check
make validate-asyncapi                         # official schema/parser on exported fixtures and every docs example document
make js-test browser-test                      # Vitest and Playwright Chromium
make installed-test PYTHON_VERSION=3.12 [LITESTAR_BOUNDARY=latest]
make browser-test-installed PYTHON_VERSION=3.12

# documentation
make docs                                      # Zensical strict build, legacy redirects, artifact and internal link verification (.venv-docs, Python 3.12)
make docs-serve                                # live preview
make docs-linkcheck                            # external links with lychee; skips when lychee is absent
make docs-clean                                # remove site/ and docs/_generated/
```

The coverage floor in `addopts`[^addopts] applies only to whole-suite runs; `make test` and `make check-all` enforce it. Coverage traces both `multiprocessing` and `thread`, so handlers run in the `TestClient` worker thread are measured. CI splits these gates into `prek`, `mypy`, `pyright`, `slotscheck`, tested-distribution and per-Python test jobs[^ci].

## Direct Markdown Continuity & Execution Loop

1. Resolve `.agents/setup-state.json` (default `.agents/bundles/`), read `index.md`, and inspect active `specs/<flow_id>/spec.md` and `tasks/<id>-<slug>.md`.
2. Run the 5-check preflight (`dependencies_closed`, `worksheet_complete`, `verification_strategy_declared`, `plan_identity_matches`, `target_symbols_exist`) before claiming the ready `pending`/`open` task.
3. Execute one vertical-slice worksheet per isolated executor turn (`model: inherit`), verify exit code `0`, stage only task-owned paths, create one atomic signed commit, and update task frontmatter (`state: completed`, `commit: <sha>`) and `spec.md` (`- [x] [<sha>] ...`).
4. Run `/flow:learn` at any time to reconcile drift, harvest mid-flow discoveries, resynthesize `.agents/bundles/knowledge/**`, and synchronize `.agents/skills/` and `.agents/agents/`.

## Verification Strategies

| Strategy | Select for | Required evidence |
| --- | --- | --- |
| `behavior_tdd` | New observable behavior | Focused `--no-cov` test fails because behavior is absent; minimal implementation makes it green. |
| `regression_tdd` | Defect correction | Focused reproduction demonstrates the defect; the narrow fix makes it green. |
| `characterization` | Behavior-preserving refactor/deletion | Green focused baseline before and unchanged behavior after. |
| `static_validation` | Manifest, config, workflows, tooling | Native parser/lint/type/build; an isolated violation proves a new gate fails with the expected diagnostic. |
| `documentation_validation` | Links, examples, docs structure | `make docs docs-linkcheck validate-pep723` and `uv run pytest src/tests/unit/docs -q --no-cov` before and after. |
| `integration_acceptance` | Composition of existing contracts | Green baseline; end-to-end scenario (official validator, browser or installed wheel) plus injected negative states. |

Never manufacture a failing unit test for documentation, configuration, generated assets or behavior-preserving cleanup.

## Commits

Use `<type>(<scope>): <summary>` and stage exact paths. Never stage broadly in a dirty checkout. Commits stay local unless the user authorizes publication. `make release` bumps versions without committing or tagging; tagging remains a user action.

[^make]: `Makefile`
[^addopts]: `pyproject.toml::tool.pytest.ini_options`
[^ci]: `.github/workflows/ci.yml`
