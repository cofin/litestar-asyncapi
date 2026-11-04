---
type: Task
id: schema-fixes:t04
title: Readable schema errors naming only the failing payload
state: completed
priority: P3
verification_strategy: behavior_tdd
depends_on: [schema-fixes:t03]
files:
  - src/litestar_asyncapi/asyncapi/schema_generation/schema.py
  - docs/changelog.rst
tests:
  - src/tests/unit/schema_generation/test_native.py
plan_revision: 3
plan_commit: 5f1a5e7
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:59:51Z
last_verified_commit: b26dfda
verification_evidence: "RED: generate message nested '500:' and printed FieldDefinition/ParameterKwarg; components message listed every payload and not the component. GREEN: make lint 0, make type-check 0, make test 0 (228 passed, 93.91%), make validate-asyncapi 0"
created_at: 2026-11-04T17:52:38Z
updated_at: 2026-11-04T17:59:51Z
commit: 23b8fb5
tags: [schema, errors]
---

# Readable schema errors naming only the failing payload

## Objective

`AsyncAPISchemaGenerator` errors read as one message: no nested `500:` prefixes, a short annotation instead of a full `FieldDefinition`/`ParameterKwarg` repr, and `components()` names only the payload whose component failed.

## Context

- **Why `behavior_tdd`.** Visible in the `ImproperlyConfiguredException` text raised by `generate` and `components`.
- **Fix location.** `asyncapi/schema_generation/schema.py::AsyncAPISchemaGenerator`. Use `error.detail` for wrapped `ImproperlyConfiguredException`s. Keep each generated output with its origin, and when a component fails to export, name the component and the origins whose outputs reference it directly or through other components.
- **Existing contract.** Messages still name the payload and its provenance (`test_distribution.py` matches `Cannot generate AsyncAPI payload.*str.*route /events`).

## Steps

1. **RED.** In `src/tests/unit/schema_generation/test_native.py` assert a single `500:` prefix and no `FieldDefinition(` repr in a `generate` failure, and that a `components()` failure names the failing component's payload but not an unrelated one.
2. **GREEN.** Update `AsyncAPISchemaGenerator.generate` and `components`.
3. **Docs.** Add a plain-language line under Fixed in `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/unit/schema_generation/test_native.py -q --no-cov` fails on the new tests.
- **Final:** `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] `generate` errors carry one status prefix and a short annotation.
- [x] `components()` errors name only the payload origins that reach the failing component.
- [x] Existing provenance assertions stay green.

## Notes & Discoveries

- [2026-11-04 17:59] Origins are stored per output; `components()` names the failing component and the payloads whose outputs reference it directly or through other components.
- [2026-11-04 17:59] First lint run failed on ruff EM102/TRY003 for an f-string in `raise`; fixed by building `detail` first.
