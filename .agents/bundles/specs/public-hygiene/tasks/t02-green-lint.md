---
type: Task
id: public-hygiene:t02
title: Green the lint gate and remove planning labels
state: pending
priority: P0
verification_strategy: static_validation
depends_on: [public-hygiene:t01]
files:
  - pyproject.toml
  - src/litestar_asyncapi/spec/security_scheme.py
  - src/tests/fixtures/asyncapi/README.md
tests: []
plan_revision: 4
plan_commit: 691324d
state_revision: 0
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: null
last_verified_commit: null
verification_evidence: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
commit: null
tags: [hygiene, lint]
---

# Green the lint gate and remove planning labels

## Objective

`make lint` and `make type-check` pass with no configuration warnings, and tracked source, tests and fixtures contain no planning labels (R3, R4).

## Context

- **Why `static_validation`.** These are configuration, comment and prose changes, and package behavior stays the same. `make test` confirms that.
- **Codespell.** `addopt` is the stem codespell reports for the pytest key `addopts`. Ignoring it is narrower than skipping `.agents/`.
- **Skill:** `asyncapi-release-ci`.

## Steps

1. **Baseline.** Run `make lint` and confirm that codespell fails only on `addopt`, in every `.agents/` file that quotes the pytest key, this plan included. Run `make type-check` and confirm it prints `Unrecognized option: warn_untyped_fields`.
2. **`pyproject.toml::tool.codespell`.** Set `ignore-words-list = ["addopt", "asyncapi"]`.
3. **`pyproject.toml::tool.pydantic-mypy`.** Delete the `warn_untyped_fields = true` line.
4. **`src/litestar_asyncapi/spec/security_scheme.py::SecurityScheme`.** Delete the inline comment above `flows`. Typed OAuth flows are backlog in the Master PRD, so nothing replaces it.
5. **`src/tests/fixtures/asyncapi/README.md`.** Replace the sentence "Task 5.1 will connect CLI-generated documents to this gate; these fixtures are intentionally independent contracts." with: "`make validate-asyncapi` also exports `tests.fixtures.apps.cli:app` through the CLI and validates the result; these fixtures remain independent hand-written contracts."
6. **Final check.** Re-run the gates.

## Verification

- **Initial:**
  - `make lint` exits non-zero at codespell.
  - `make type-check 2>&1 | grep -c "Unrecognized option"` prints `1`.
- **Final:**
  - `make lint` exits `0`, with every prek hook passing and every later lint step running.
  - `make type-check 2>&1 | grep -c "Unrecognized option"` prints `0`, and the command exits `0`.
  - `git grep -nE "Task [0-9]+\.[0-9]+|PRD-[0-9]+" -- src tools docs` exits `1`.
  - `uv run pytest src/tests -q --no-cov` passes.

## Acceptance Criteria

- [ ] R3: `make lint` exits `0`.
- [ ] R4: no planning labels in `src`, `tools` or `docs`.
- [ ] mypy reports no unrecognized configuration options.

## Notes & Discoveries
