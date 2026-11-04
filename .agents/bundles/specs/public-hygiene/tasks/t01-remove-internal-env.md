---
type: Task
id: public-hygiene:t01
title: Remove internal environment detection and setup script
state: completed
priority: P0
verification_strategy: static_validation
depends_on: []
files:
  - Makefile
  - tools/scripts/setup-env.sh
  - .gitignore
  - .agents/bundles/log.md
tests: []
plan_revision: 4
plan_commit: 691324d
state_revision: 1
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:37:12Z
last_verified_commit: null
verification_evidence: "name grep exit 1; install dry-run has no setup-env; Makefile.local override sourced from file; type-check, slotscheck, zizmor and example validators exit 0"
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
commit: null
tags: [hygiene, makefile]
---

# Remove internal environment detection and setup script

## Objective

No tracked file names the internal environment. `make install` works from the default index, and a private override is still possible through git-ignored files (R1, R2).

## Context

- **Why `static_validation`.** The change removes build configuration and has no runtime behavior to test. The gates are `git grep` and `make -n` dry runs.
- **Invariant.** `make install` keeps its other prerequisites (`destroy clean`) and steps unchanged.
- **Skill:** `asyncapi-release-ci`.
- **Do not repeat the name.** Never write the internal environment's name in the commit message, task notes or any new file. Refer to it only as "the internal environment".

## Steps

1. **Baseline.** Record that `git grep -il "<name>"` lists `Makefile`, `tools/scripts/setup-env.sh` and `.agents/bundles/log.md`. Take the name from those files, not from this worksheet.
2. **Makefile, variable section.** Delete the comment line naming the OS and the whole `ifneq … endif` block that exports `PIP_INDEX_URL`/`UV_INDEX_URL`. In its place, directly after `UV_SYNC_ARGS ?= …`, add `-include Makefile.local`. Overrides in that file must use `:=` or `export VAR := …`. `?=` cannot override variables that are already set above the include.
3. **Makefile, `setup-env`.** Delete the `.PHONY: setup-env` line and the `setup-env` target with its recipe.
4. **Makefile, `install`.** Change the prerequisites from `destroy clean setup-env` to `destroy clean`.
5. **Delete `tools/scripts/setup-env.sh`.** `tools/scripts/` contains nothing else, so delete the directory too.
6. **`.gitignore`.** Append `Makefile.local` and `uv.toml` under a `# Local developer overrides` heading.
7. **`.agents/bundles/log.md`.** In the "Modernized `Makefile`" bullet of the 2026-09-20 "Modernize Project Tooling, CI, and Configuration" entry, delete the list item that names the OS detection, including its trailing comma. This one-time redaction is the only exception to the log's append-only rule.

## Verification

- **Initial:** `git grep -il "<name>"` exits `0` and lists three files.
- **Final:**
  - `git grep -il "<name>"` exits `1`.
  - `make -n install | grep -c setup-env` prints `0`.
  - `make help | grep -c setup-env` prints `0`.
  - `env -u UV_INDEX_URL -u PIP_INDEX_URL make -p -n help 2>/dev/null | grep -c "from 'Makefile.local'"` prints `0` with no `Makefile.local`.
  - `printf 'export UV_INDEX_URL := https://example.invalid/simple\n' > Makefile.local; env -u UV_INDEX_URL -u PIP_INDEX_URL make -p -n help 2>/dev/null | grep -B1 '^UV_INDEX_URL' | grep -c "from 'Makefile.local'"; rm Makefile.local` prints `1`, which shows the value comes from the file and not the shell.
  - `git status --short` shows no `Makefile.local`.
  - `make type-check slotscheck zizmor validate-examples validate-pep723` exits `0`. prek still fails only at codespell, which `t02` fixes. `make lint` stops at the first failing prerequisite, so these steps are run separately.

## Acceptance Criteria

- [x] R1: no tracked file names the internal environment.
- [x] R2: `install` no longer depends on `setup-env`. `Makefile.local` is optional, git-ignored and loaded when present.
- [x] The script and the `tools/scripts/` directory are removed.

## Notes & Discoveries
