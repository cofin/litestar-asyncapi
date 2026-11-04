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

Verified on this host (uv 0.13, GNU Make 4.4, Node via npm). Prefer `Makefile` targets[^make]; run Python tools through `uv run`.

```bash
# setup
make install                                   # uv sync --all-extras --dev
make js-install                                # npm ci (Node (`.nvmrc`); build/test only)

# focused test (red-capable)
uv run pytest src/tests/unit/test_generator.py::test_name -q --no-cov

# lint & typecheck
make lint                                      # prek, type-check, slotscheck, zizmor, validate-examples, validate-pep723
make type-check                                # mypy src && pyright
make slotscheck
make fix                                       # ruff autofix + format

# full verification gate
make check-all                                 # lint, test-all, coverage
make build validate-asyncapi js-test browser-test
make installed-test PYTHON_VERSION=3.12 [LITESTAR_BOUNDARY=latest]
make browser-test-installed PYTHON_VERSION=3.12

# documentation
make docs docs-linkcheck docs-audit
```

The coverage floor in `addopts`[^addopts] applies only to whole-suite runs; `make test` and `make check-all` enforce it. CI splits these gates into `prek`, `mypy`, `pyright`, `slotscheck`, tested-distribution and per-Python test jobs[^ci].

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
| `documentation_validation` | Links, examples, docs structure | `make docs docs-linkcheck validate-examples validate-pep723` before and after. |
| `integration_acceptance` | Composition of existing contracts | Green baseline; end-to-end scenario (official validator, browser or installed wheel) plus injected negative states. |

Never manufacture a failing unit test for documentation, configuration, generated assets or behavior-preserving cleanup.

## Commits

Use `<type>(<scope>): <summary>` and stage exact paths. Never stage broadly in a dirty checkout. Commits stay local unless the user authorizes publication. `make release` bumps versions without committing or tagging; tagging remains a user action.

[^make]: `Makefile`
[^addopts]: `pyproject.toml::tool.pytest.ini_options`
[^ci]: `.github/workflows/ci.yml`
