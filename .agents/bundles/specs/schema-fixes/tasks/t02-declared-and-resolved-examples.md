---
type: Task
id: schema-fixes:t02
title: Read declared examples behind Optional and for named payload annotations
state: completed
priority: P2
verification_strategy: behavior_tdd
depends_on: [schema-fixes:t01]
files:
  - src/litestar_asyncapi/_compat.py
  - src/litestar_asyncapi/asyncapi/generator.py
  - docs/changelog.rst
tests:
  - src/tests/unit/extractors/test_example_precedence.py
plan_revision: 3
plan_commit: 5f1a5e7
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:59:51Z
last_verified_commit: 89c0796
verification_evidence: "RED: Optional declared-examples test hit the generation guard; named-payload test raised the 'Unsupported type' warning. GREEN: make lint 0, make type-check 0, make test 0 (225 passed, 93.78%), make validate-asyncapi 0"
created_at: 2026-11-04T17:52:38Z
updated_at: 2026-11-04T17:59:51Z
commit: 2875411
tags: [schema, examples]
---

# Read declared examples behind Optional and for named payload annotations

## Objective

A payload `Optional[P]` uses `P`'s declared examples (audit B9), and a string payload annotation resolved through the app's `signature_namespace` gets a generated example instead of an "Unsupported type" warning (audit B10).

## Context

- **Why `behavior_tdd`.** Both bugs are visible in the message `examples` of the generated document.
- **Fix location.** `_compat.py::declared_schema_examples` unwraps a single-member `Optional` before reading examples. `asyncapi/generator.py::_build_message` builds the example field with `resolve_annotation(definition.payload, app)` instead of `FieldDefinition.from_annotation`.
- **Precedence stays:** explicit message examples > declared schema/model examples > generated example.
- **Shared file.** `_compat.py` and `generator.py` are also edited by the next chapter; keep the edits local to these two functions.

## Steps

1. **RED.** In `src/tests/unit/extractors/test_example_precedence.py` add a test for declared Pydantic examples behind `Optional[P]` and a test for a string payload resolved through `Litestar(signature_namespace=...)`.
2. **GREEN.** Apply the two local fixes.
3. **Docs.** Add plain-language lines under Fixed in `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/unit/extractors/test_example_precedence.py -q --no-cov` fails on the new tests.
- **Final:** `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] `Optional[P]` payloads use `P`'s declared examples.
- [x] String payload annotations get generated examples without a warning.
- [x] The changelog records both fixes.

## Notes & Discoveries

- [2026-11-04 17:57] B10 needs an app-level `Litestar(signature_namespace=...)`; `resolve_annotation` reads only the app namespace, as the schema path already did.
- [2026-11-04 17:57] `generator.py` change is one call in `_build_message` plus the `resolve_annotation` import.
