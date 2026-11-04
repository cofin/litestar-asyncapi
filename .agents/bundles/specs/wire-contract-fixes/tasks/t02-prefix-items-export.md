---
type: Task
id: wire-contract-fixes:t02
title: Export explicit Schema.prefix_items as Draft07 tuple items
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [wire-contract-fixes:t01]
files:
  - src/litestar_asyncapi/_draft07.py
  - src/litestar_asyncapi/spec/schema.py
  - src/litestar_asyncapi/asyncapi/schema_generation/dialect.py
  - src/tests/fixtures/apps/bindings.py
  - src/tests/fixtures/asyncapi/bindings-3.0.0.json
  - src/tests/fixtures/asyncapi/bindings-3.1.0.json
  - docs/changelog.rst
tests:
  - src/tests/unit/spec/test_wire_contract.py
  - src/tests/unit/schema_generation/test_dialect.py
  - src/tests/integration/test_cli.py
plan_revision: 3
plan_commit: 938a9e1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:48:54Z
last_verified_commit: aba7e97
verification_evidence: "RED: 2 new prefix_items wire tests failed and the bindings export contained prefixItems. GREEN: make lint 0, make type-check 0, make test 0 (221 passed, 93.74%), make validate-asyncapi 0 (7 documents validated)"
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T17:48:54Z
commit: null
tags: [conformance, draft07, tuples]
---

# Export explicit Schema.prefix_items as Draft07 tuple items

## Objective

No emitted document contains `prefixItems`: an explicit `Schema(prefix_items=...)` serializes to a Draft07 `items` array, with `items` moving to `additionalItems` (audit B6; Master Decision 3).

## Context

- **Why `behavior_tdd`.** B6 is visible through `Schema.to_schema` and the generated document.
- **Shared rule, no cycle.** The keyword mapping moves out of `asyncapi/schema_generation/dialect.py` into the dependency-free `src/litestar_asyncapi/_draft07.py::tuple_item_keywords`. `spec/schema.py` cannot import `dialect.py` (the `asyncapi` package imports `spec`), and calling `to_asyncapi_schema` would also rewrite `$defs`/`$ref`.
- **Error contract.** `Schema.to_schema` raises `ValueError` when `items`, `additional_items` and `prefix_items` are all set, or when `items` is a list beside `prefix_items`. `dialect.py` keeps its stricter rejection of `additionalItems` beside `prefixItems` and reports helper errors as `ImproperlyConfiguredException` with the schema path.
- **Skills:** `asyncapi-schema` (`spec/schema.py`, dialect helper).

## Steps

1. **RED.** Add tests in `src/tests/unit/spec/test_wire_contract.py` for `Schema(prefix_items=...)` alone, with `items`, with `additional_items`, nested inside another `Schema`, and the `ValueError` path (message matched). Add an explicit `Schema(prefix_items=...)` payload to `src/tests/fixtures/apps/bindings.py` and assert in `src/tests/integration/test_cli.py` that the generated documents contain no `prefixItems`.
2. **GREEN.** Add `_draft07.py::tuple_item_keywords`, override `spec/schema.py::Schema.to_schema` to apply it, and switch `dialect.py::_Converter.keyword` to the helper. Regenerate the fixtures.
3. **Docs.** Add the `prefix_items` export entry under Fixed in `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/unit/spec/test_wire_contract.py -q --no-cov` fails on the new `prefix_items` tests.
- **Final:** `uv run pytest src/tests/unit/spec src/tests/unit/schema_generation src/tests/integration/test_cli.py -q --no-cov`, `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] `Schema(prefix_items=...)` emits Draft07 `items`/`additionalItems` and never `prefixItems`.
- [x] Setting `items`, `additional_items` and `prefix_items` together raises `ValueError`.
- [x] `dialect.py` and `Schema.to_schema` share one mapping helper with no import cycle; existing dialect tests stay green.
- [x] The changelog records the `prefix_items` export fix.

## Notes & Discoveries

- [2026-11-04 17:48] The helper lives at `src/litestar_asyncapi/_draft07.py` and imports nothing from the package, so both `spec/schema.py` and `dialect.py` use it without a cycle.
- [2026-11-04 17:48] `dialect.py` reports helper errors at the `items` path, matching its previous message location; a new `test_dialect.py` test pins the path and message. Its stricter rejection of `additionalItems` beside `prefixItems` is unchanged.
- [2026-11-04 17:48] `Schema.to_schema` calls `BaseSchemaObject.to_schema(self)` explicitly because zero-argument `super()` is unreliable on `slots=True` dataclasses before Python 3.14.
- [2026-11-04 17:48] The bindings fixture gained an explicit tuple payload (`positions` channel), and the drift test asserts no `prefixItems` in either export.
