---
type: Spec
flow_id: public-hygiene
title: Remove Leaked Internals and Green the Lint Gate
description: Remove internal environment names and stale planning labels from tracked files and make make lint pass.
state: active
parent_prd: contract-fixes
research: []
plan_revision: 4
plan_commit: 691324d
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [hygiene, release-ci, lint]
---

# Remove Leaked Internals and Green the Lint Gate

## 1. Specification & Context

### 1.1 Upstream Execution Baseline

- Branch `feat/updates-1`, based on `691324d`.
- `make test` (212 passed) and `make type-check` pass.
- `make lint` fails at the codespell hook.

### 1.2 Code Analysis Summary

| Target | Current state |
| --- | --- |
| `Makefile` (top-level variable section) | An `ifneq` block detects an internal OS through `/etc/os-release` and exports `PIP_INDEX_URL`/`UV_INDEX_URL`. Both URLs point at public PyPI. The comment above the block names the OS. |
| `Makefile::setup-env` | Its help text names the internal OS, and the target runs `tools/scripts/setup-env.sh`. |
| `Makefile::install` | Lists `setup-env` among its prerequisites (`destroy clean setup-env`). |
| `tools/scripts/setup-env.sh` | The only file in `tools/scripts/`. It names the internal OS and writes `uv.toml`. |
| `.gitignore` | Ignores neither `uv.toml` nor `Makefile.local`. Neither file is tracked. |
| `.agents/bundles/log.md` | The 2026-09-20 "Modernize Project Tooling, CI, and Configuration" entry names the internal OS. |
| `pyproject.toml::tool.codespell` | `ignore-words-list = ["asyncapi"]`, so the pytest key `addopts` is flagged as `addopt` in every `.agents/` document that quotes it, this plan included. |
| `pyproject.toml::tool.pydantic-mypy` | Sets `warn_untyped_fields`, which pydantic-mypy rejects as an unrecognized option. |
| `src/litestar_asyncapi/spec/security_scheme.py::SecurityScheme` | An inline comment above `flows` carries a planning label. Project rules ban inline comments. |
| `src/tests/fixtures/asyncapi/README.md` | Says "Task 5.1 will connect CLI-generated documents to this gate". That is a stale planning label: `Makefile::validate-asyncapi` already validates the CLI-exported `tests.fixtures.apps.cli:app`. |

### 1.3 Relevant Patterns

- `.agents/bundles/knowledge/patterns/ci-supply-chain.md` (Makefile and gate conventions)
- `.agents/bundles/knowledge/workflow.md` (canonical commands)
- Skill: `asyncapi-release-ci`

## 2. Requirements

### 2.1 Functional Requirements

- **R1.** No tracked file names the internal environment.
- **R2.** `make install` resolves from the default package index on a machine with no private configuration. A git-ignored `Makefile.local`, loaded with `-include`, or a git-ignored `uv.toml` can still override the index.
- **R3.** `make lint` passes.
- **R4.** Tracked source, tests and fixtures contain no planning labels.

### 2.2 Non-Functional & Safety Constraints

- History is not rewritten (Master Decision 1).
- `log.md` gets a one-time redaction of a single entry, the only exception to its append-only rule.
- No package code changes behavior. The `security_scheme.py` change removes a comment only.

### 2.3 Acceptance Scenarios

- **Given** a clean checkout, **when** `git grep -i` runs for the environment name, **then** it exits `1` with no matches.
- **Given** no `Makefile.local`, **when** `make -n install` runs, **then** the output contains no `setup-env` and no index export.
- **Given** a `Makefile.local` that sets `export UV_INDEX_URL := ...`, **when** `make -p -n help` runs with the shell variable unset, **then** `UV_INDEX_URL` is reported as coming from `Makefile.local`.
- **Given** the tree, **when** `make lint` runs, **then** it exits `0`.

### 2.4 Alternatives Considered

- **Keep a neutral, opt-in `setup-env` target.** Rejected: a public target that exists only for one private machine is still unneeded surface. `-include Makefile.local` covers the need with no tracked code.
- **Rename the occurrences instead of removing them.** Rejected: the OS detection is the leak itself.

## 3. Requirement-to-Task Traceability Matrix

| Requirement | Owning Task | Verification Strategy | Gate |
| --- | --- | --- | --- |
| R1, R2 | `t01` | `static_validation` | `git grep -i`, `make -n install`, `make help` |
| R3, R4 | `t02` | `static_validation` | `make lint`, `make type-check`, `git grep` for planning labels |

## 4. Implementation Plan

### Phase 1

- [x] t01 — remove internal environment detection and setup script (tasks/t01-remove-internal-env.md)
- [ ] t02 — green the lint gate and remove planning labels (tasks/t02-green-lint.md)

**Phase 1 Recovery Checkpoint:** `make lint && make type-check && make test` exits `0`, and `git grep -il` for the environment name prints nothing.

## 5. Continuity Snapshot

- **State:** planned. No task has started.
- **Decisions:** removal from the tree only; private index overrides go in a git-ignored `Makefile.local` or `uv.toml`.
- **Review:** round 1 of the independent review is adjudicated. All 6 findings were adopted, and `plan_revision` is now 4.
- **Discoveries:** the index URLs are public PyPI, so only the environment name is sensitive. No git hooks are installed, so `t01` can be committed while codespell still fails.
