---
type: Task
id: contract-ergonomics:t05
title: Readable contract examples, docs and schema-name parity
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [t04]
files:
  - docs/examples/contracts.py
  - docs/examples/secured_orders.py
  - docs/integrations/channels-plugin.md
  - docs/integrations/index.md
  - docs/integrations/security-and-servers.md
  - docs/learn/decorators.md
  - docs/learn/examples.md
  - docs/learn/export.md
  - docs/learn/websocket-handlers.md
  - docs/project/migration.md
tests:
  - src/tests/unit/schema_generation/test_native.py
plan_revision: 2
plan_commit: 36294c1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T04:10:00Z
last_verified_commit: 5678474
verification_evidence: "Parity test passed on first run (characterization: names match, including first_Item/second_Item and module-qualified local types). make lint 0 (incl. validate-pep723), make type-check 0, make test 0 (316 passed, 97.04%), make validate-asyncapi 0 (25 documents incl. docs/_generated/secured_orders.json), make docs 0 (Zensical strict, budgets verified)"
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T04:10:00Z
commit: 5678474
tags: [docs, examples, schema, tdd]
---

# Readable contract examples, docs and schema-name parity

## Objective

Replace the all-features contract example with a typed broker request/reply for Learn, add a JWTAuth-based advanced example for the security page, update the pages, changelog and migration notes, and pin that AsyncAPI component schema names match Litestar OpenAPI names for the same Python types (R6, R7).

## Context

- **Why `behavior_tdd`.** R7 is a new pinned behavior; the docs part is validated by `make docs`, `make validate-pep723` and the executed-example tests.
- **Invariants.** Examples keep a module-level `app`, a PEP 723 block with `requires-python = ">=3.11"`, and no inline comments. The reply channel has its own `send` operation. Payload `$ref`s stay under `#/components/schemas`. Pages include generated fragments from `docs/_generated/`.
- **Canonical tests.** `src/tests/unit/schema_generation/test_native.py` for parity; `src/tests/unit/docs/test_examples.py` executes every example.

## Steps

1. Write the parity test (RED if names diverge) for dataclass, msgspec, Pydantic and nested types.
2. Rewrite `docs/examples/contracts.py`, add `docs/examples/secured_contracts.py`, update the pages, changelog and migration notes.
3. Run gates.

## Verification

- **Initial:** `uv run pytest src/tests/unit/schema_generation/test_native.py -q --no-cov`.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi`, `make docs` exit `0`.

## Acceptance Criteria

- [x] R6: simple typed request/reply example with a reply `send` operation; JWTAuth example with `security=["BearerToken"]`, a trait shared by two operations and a correlation ID; pages, servers sentence, changelog and migration updated.
- [x] R7: schema-name parity is pinned by a test.

## Notes & Discoveries

- [2026-11-05 03:35] R7 holds without code changes: AsyncAPI and Litestar OpenAPI produce the same six component names for dataclass, msgspec, Pydantic, recursive and same-short-name types.
- [2026-11-05 03:45] The advanced example is `docs/examples/secured_orders.py` (`litestar[standard,jwt]` in its PEP 723 block); `JWTAuth(exclude=["/asyncapi", "/schema"])` keeps the docs routes reachable in the executed-example test.
- [2026-11-05 03:50] The request/reply walkthrough moved to Learn › Decorators (`#contracts-without-a-route`); links that pointed at the removed `#explicit-broker-traits-and-replies` anchor now point there. The security page leads with the JWTAuth example and a conversion table.
