---
type: Spec
flow_id: wire-contract-fixes
title: Wire Keys and Conformance Fixture
description: Make spec wire-key normalization alias-driven, export prefixItems as Draft07, and add a bindings, security, traits and extensions fixture to official validation.
state: active
parent_prd: contract-fixes
research: []
plan_revision: 3
plan_commit: 938a9e1
state_revision: 0
current_task: t02
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [spec, conformance, validation]
---

# Wire Keys and Conformance Fixture

## Charter

Fix the two places where wire models emit invalid or ignored keys (audit B1, B6). Close the validator blind spot that let them through. Domain skills: `asyncapi-generation` for `spec/**`, and `asyncapi-schema` for `spec/schema.py`.

## Upstream Dependencies

- `public-hygiene`: lint must already be green.

## Key Deliverables

- **Conformance fixture first.** Build a fixture app that uses Kafka and AMQP bindings and `x-` extensions on the root, info, channel, operation and message objects. Generate `src/tests/fixtures/asyncapi/bindings-3.0.json` and `bindings-3.1.json` from it with the existing `export-asyncapi-fixture` path, one per spec version, and validate both with `tools/validate_asyncapi.mjs`. The fixture must fail before the B1 fix. The existing hand-written fixtures already cover security schemes, traits and `ws` bindings.
- **`spec/base.py::_normalize_key`** follows Master Decision 4. Existing aliases already cover `Schema` and `SecurityScheme.in_`. Add a regression test for the `_compat.py::normalize_native_schema` caller.
- **`Schema.to_schema`** follows Master Decision 3. It uses the shared `prefixItems` helper moved out of `dialect.py`, not `to_asyncapi_schema`.
- **Changelog.** Record the Kafka key correction as a breaking fix.
- **Tests.** Regression tests in `src/tests/unit/spec/test_wire_contract.py` cover the Kafka server and message keys, an alias-less field ending in `_in`, and the `prefix_items` export.

## Public Seams

- `litestar_asyncapi.spec` models via `BaseSchemaObject.to_schema`
- `make validate-asyncapi`

## Acceptance Boundary

- `make validate-asyncapi` validates the new fixture for both spec versions.
- The Kafka binding keys match the official kafka 0.5.0 binding schema.
- No emitted document contains `prefixItems`.

## Implementation Plan

- [x] t01 — official Kafka keys, alias-driven key normalization and the bindings conformance fixture (tasks/t01-kafka-keys-and-conformance-fixture.md)
- [ ] t02 — export explicit `Schema.prefix_items` as Draft07 tuple items (tasks/t02-prefix-items-export.md)

**Recovery checkpoint:** `make lint && make type-check && make test && make validate-asyncapi` exits `0`.

## Continuity Snapshot

- **Fixture naming.** The fixtures follow the existing `<name>-<full version>.json` convention: `bindings-3.0.0.json` and `bindings-3.1.0.json`.
- **Extension reach.** Root and `info` extensions cannot be set through `AsyncAPIConfig` (Master PRD backlog), so the generated fixture covers extensions on servers, messages, traits and `components` channel/operation entries instead.
- **Task split.** The fixture and the key fix share one task: the fixture is the gate-level failing check for B1, and committing it alone would leave `make validate-asyncapi` red.
