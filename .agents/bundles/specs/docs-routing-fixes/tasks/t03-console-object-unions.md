---
type: Task
id: docs-routing-fixes:t03
title: Open the console for nullable objects and object unions
state: completed
priority: P2
verification_strategy: regression_tdd
depends_on: []
files:
  - tools/frontend/interactive.ts
  - src/litestar_asyncapi/assets/ui/**
  - docs/usage/renderers.rst
  - docs/changelog.rst
tests:
  - tools/frontend/tests/interactive.test.ts
plan_revision: 3
plan_commit: 91b5852
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:21:00Z
last_verified_commit: bb88760
verification_evidence: "RED: interactive.test.ts 'accepts nullable object types and object unions' failed at type ['object','null']. Cycle guard mutation-checked (RangeError without it). GREEN with Node 26.13.0: make js-build reproduced HEAD assets byte-identically before the change; make js-test 0 (12 passed), make browser-test 0 (19 passed, Chromium); make lint 0, make type-check 0, make test 0 (242 passed, 94.50%), make validate-asyncapi 0"
created_at: 2026-11-04T18:17:00Z
updated_at: 2026-11-04T18:22:00Z
commit: bb88760
tags: [docs-ui, console, frontend]
---

# Open the console for nullable objects and object unions

## Objective

`supportsWire` accepts JSON-text payloads typed `[object, null]` and top-level `oneOf`/`anyOf` unions whose members are all objects or arrays; scalar members, null-only types and circular unions still decline (audit B13, verify first).

## Context

- **Why `regression_tdd`.** B13 came from code reading; the Vitest case reproduced it (`typeof payload.type === 'string'` rejected type arrays and unions).
- **Fix.** `interactive.ts::isJsonContainer`: a string `type` must be a container; a `type` array needs at least one container and no member other than containers and `null`; otherwise every `oneOf` (or `anyOf`) member must recursively be a container, with a `WeakSet` guard against dereferenced cycles.
- **Rebuild.** Assets rebuilt with Node 26 (`.nvmrc`); HEAD sources rebuilt byte-identically first.

## Steps

1. **RED.** Accept and decline cases in `tools/frontend/tests/interactive.test.ts`, including hostile scalar, nested-scalar, binary-mode and circular `$ref` unions. Documents the parser rejects (`type: []`, `oneOf: []`) cannot reach `supportsWire` and were dropped.
2. **GREEN.** `isJsonContainer`; `make js-build`.
3. Update `docs/usage/renderers.rst` and the changelog.

## Verification

- **Initial:** `npx vitest run tools/frontend/tests/interactive.test.ts` fails on `type: ['object','null']`.
- **Final:** `make js-test`, `make browser-test`, `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] `type: [object, null]`, `oneOf` of objects and `anyOf` of object/array open the console.
- [x] Unions or type arrays with scalar members, `type: [null]` and circular unions decline.
- [x] Committed assets match a Node 26 rebuild.

## Notes & Discoveries

- [2026-11-04 18:19] Without the cycle guard a self-referencing `oneOf` overflows the stack.
- [2026-11-04 18:19] Per the charter, a `oneOf` with a `{type: null}` member still declines; only type arrays may carry `null`.
