---
type: Task
id: wire-contract-fixes:t01
title: Official Kafka keys, alias-driven key normalization and the bindings conformance fixture
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: []
files:
  - src/litestar_asyncapi/spec/base.py
  - src/litestar_asyncapi/_compat.py
  - src/tests/fixtures/apps/bindings.py
  - src/tests/fixtures/asyncapi/bindings-3.0.0.json
  - src/tests/fixtures/asyncapi/bindings-3.1.0.json
  - src/tests/fixtures/asyncapi/README.md
  - Makefile
  - docs/changelog.rst
tests:
  - src/tests/unit/spec/test_wire_contract.py
  - src/tests/unit/spec/test_base.py
  - src/tests/unit/schema_generation/test_native.py
  - src/tests/integration/test_cli.py
plan_revision: 3
plan_commit: 938a9e1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T17:45:28Z
last_verified_commit: 938a9e1
verification_evidence: "RED: make validate-asyncapi exit 2 (official-schema/additionalProperties on servers/kafka/bindings/kafka and channels/orders/messages/order/bindings/kafka); 2 new wire tests failed. GREEN: make lint 0, make type-check 0, make test 0 (218 passed, 93.45%), make validate-asyncapi 0 (7 documents validated)"
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T17:45:28Z
commit: null
tags: [conformance, bindings, wire-keys]
---

# Official Kafka keys, alias-driven key normalization and the bindings conformance fixture

## Objective

Documents using Kafka and AMQP bindings and `x-` extensions pass the official AsyncAPI 3.0.0 and 3.1.0 schemas, and `make validate-asyncapi` keeps checking them (audit B1 and the validation coverage gap; Master Decision 4).

## Context

- **Why `behavior_tdd`.** B1 is a wire defect visible through `BaseSchemaObject.to_schema` and the official validator.
- **Fixture first.** The fixture app is exported through the existing `export-asyncapi-fixture` CLI path into `src/tests/fixtures/asyncapi/bindings-<version>.json`, matching the existing `websocket-3.0.0.json` naming. `tools/validate_asyncapi.mjs` already validates every committed JSON file in that directory. A drift test in `src/tests/integration/test_cli.py` keeps the committed files equal to fresh exports so `make test` fails on staleness.
- **Extension reach.** The application surface reaches `x-` extensions on servers, messages, traits and `components` entries. Root and `info` extensions are not configurable from `AsyncAPIConfig` (Master PRD backlog), so the fixture cannot carry them; `components.channels` and `components.operations` entries cover Channel and Operation extension serialization.
- **Key rule.** `spec/base.py::_normalize_key` takes the dataclass field: `metadata["alias"]` wins, otherwise `ref` becomes `$ref` and snake_case becomes camelCase. The implicit `schema_` strip and `_in` rule are deleted. `ref` stays because Litestar's own `Reference` (serialized by `_compat.py::normalize_native_schema`) has no alias.
- **Skills:** `asyncapi-generation` (spec models), `asyncapi-schema` (`normalize_native_schema` caller).

## Steps

1. **RED.** Add `src/tests/fixtures/apps/bindings.py` (`app_3_0`, `app_3_1`), export both through `Makefile::export-asyncapi-fixture`, and confirm `make validate-asyncapi` fails at `official-schema/additionalProperties` on the Kafka server and message bindings. Add failing tests in `src/tests/unit/spec/test_wire_contract.py` for Kafka server and message keys and an alias-less `*_in` field, a `normalize_native_schema` regression test in `src/tests/unit/schema_generation/test_native.py`, and the fixture drift test in `src/tests/integration/test_cli.py`.
2. **GREEN.** Rewrite `spec/base.py::_normalize_key` per Master Decision 4 and route `BaseSchemaObject.to_schema` and `_compat.py::normalize_native_schema` through it. Update `src/tests/unit/spec/test_base.py` assertions that encoded the deleted implicit rules. Regenerate the fixtures.
3. **Docs.** Add the breaking Kafka key correction under an unreleased Fixed heading in `docs/changelog.rst`; mention the bindings fixture in `src/tests/fixtures/asyncapi/README.md`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `make validate-asyncapi` exits non-zero with `official-schema/additionalProperties` on `servers/kafka/bindings/kafka` and the message Kafka binding; `uv run pytest src/tests/unit/spec/test_wire_contract.py -q --no-cov` fails on the new Kafka and `_in` tests.
- **Final:** `uv run pytest src/tests/unit/spec src/tests/unit/schema_generation src/tests/integration/test_cli.py -q --no-cov`, `make lint`, `make type-check`, `make test` and `make validate-asyncapi` all exit `0`.

## Acceptance Criteria

- [x] Kafka server and message binding keys match the official kafka 0.5.0 binding schemas.
- [x] `_normalize_key` uses `metadata["alias"]` when present and camelCase otherwise; no implicit `schema_` or `_in` rule remains.
- [x] `normalize_native_schema` has its own regression test.
- [x] `make validate-asyncapi` validates `bindings-3.0.0.json` and `bindings-3.1.0.json`, which failed before the fix.
- [x] The changelog records the Kafka key correction as a breaking fix.

## Notes & Discoveries

- [2026-11-04 17:45] `make validate-asyncapi` ran on Node 25.6.1; Node 22 was not installed and the gate passed unchanged.
- [2026-11-04 17:45] Litestar's `Reference.ref` has no alias, so the `ref` to `$ref` rule stays in `_normalize_key`; only the `schema_` and `_in` rules were removed. `test_base.py` assertions that encoded those rules now expect `schemaType` and `parameterIn`.
- [2026-11-04 17:45] The `normalize_native_schema` regression test passes before and after the change: every Litestar `Schema` field that needs a non-camelCase key already declares an alias.
- [2026-11-04 17:45] The alias type check moved into `_normalize_key`; a new test covers its `TypeError`.
