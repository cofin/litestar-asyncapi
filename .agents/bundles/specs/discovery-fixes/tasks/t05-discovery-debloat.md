---
type: Task
id: discovery-fixes:t05
title: Delete discovery code and tests reached only by synthetic input
state: completed
priority: P1
verification_strategy: characterization
depends_on: [t01, t02, t03, t04]
files:
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/asyncapi/extractors/websocket.py
  - src/litestar_asyncapi/asyncapi/extractors/channels.py
tests:
  - src/tests/integration/conftest.py
  - src/tests/integration/test_discovery.py
  - src/tests/unit/test_generator.py
  - src/tests/unit/test_decorators.py
  - src/tests/unit/extractors/test_websocket_helpers.py
  - src/tests/unit/test_decorators_storage.py
  - src/tests/unit/extractors/test_websocket_discovery_alignment.py
  - src/tests/unit/test_operation_id_hardening.py
plan_revision: 3
plan_commit: 305f2cb
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:45:00Z
last_verified_commit: 60e7915
verification_evidence: "Baseline green (241 passed; generator.py 345 stmts/21 miss, websocket.py 120/4). Guard proven against a planted duplicate (AssertionError: duplicate discovered channel keys). After: make lint 0, make type-check 0, make test 0 (242 passed, 94.50%), make validate-asyncapi 0; generator.py 92.1% -> 94%, extractors/websocket.py 95.0% -> 95.3%, channels.py 100%"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:45:00Z
commit: 60e7915
tags: [debloat, discovery, tests]
---

# Delete discovery code and tests reached only by synthetic input

## Objective

Carry out the chapter-4 rows of the Master debloat ledger without changing any document produced from a real app, and without lowering coverage of `asyncapi/generator.py` or `asyncapi/extractors/`.

## Context

- **Why `characterization`.** Behavior-preserving deletion: green before, unchanged after, coverage not lower.
- **Guard first.** An autouse integration fixture asserts that discovery never yields two channels with the same key, so the merge path in `_normalize_channels` is proven unreachable from real apps before it is deleted.
- **Ledger rows.** Delete the same-identity merge block and the per-channel operation-dedupe loop in `generator.py::_normalize_channels` (keep the duplicate-key raise); delete two monkeypatched tests and rewrite the conflict test through real routes; replace the `Reference` guard in `_populate_operations` with a typed inline-channel lookup; drop the unused `schema_generator` argument of `extractors/websocket.py::_path_parameters_to_parameters`; simplify `_is_none_return_type` and `_should_include_handler`; replace `unit/extractors/test_websocket_helpers.py` with public-seam cases; merge `test_decorators_storage.py`, `test_websocket_discovery_alignment.py` and `test_operation_id_hardening.py` into canonical files. Keep `extract_websocket_channels(config=None)`.

## Steps

1. **Baseline.** `make test` green; record per-file coverage.
2. Add the integration guard; run the suite green.
3. Add public-seam replacements, then delete or merge the private-call and single-purpose test files.
4. Delete and simplify the production code listed above.
5. **Verify** coverage and gates.

## Verification

- **Initial:** `make test` exits `0` (228 passed; generator.py 92%, extractors/websocket.py 94%).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`; generator and extractor coverage at or above baseline.

## Acceptance Criteria

- [x] Integration guard proves discovered channel keys are unique.
- [x] Merge block and operation-dedupe loop are deleted; the duplicate-key raise remains and is tested through real routes.
- [x] No test monkeypatches an extractor to produce impossible input.
- [x] Merged test files are gone and their cases live in canonical files.
- [x] Coverage of `asyncapi/generator.py` and `asyncapi/extractors/` is not lower than baseline.

## Notes & Discoveries

- [2026-11-04 18:35] The integration suite had no ChannelsPlugin or config-channel app, so `test_every_discovery_source_yields_one_channel_per_key` was added to give the guard every source.
- [2026-11-04 18:36] Real routes can yield duplicate keys (two handlers on one path, a listener on a ChannelsPlugin path) but never share a route identity, so the merge block was dead while the duplicate-key raise is live; the conflict test now uses two listeners on `/same`. The error text drops the route-identity clause.
- [2026-11-04 18:40] Deleting the monkeypatched tests uncovered the shared-message conflict raise in `_populate_operations`; `test_same_named_message_is_shared_or_rejected_across_operations` covers it through a real raw socket.
- [2026-11-04 18:40] `_is_none_return_type` became `FieldDefinition.is_none_type`; native listeners always normalize a `None` return to `NoneType`.
- [2026-11-04 18:44] Stale skill and knowledge statements (route-identity merge, deleted test files and helpers, metadata order, `_coerce_action`) were corrected in the bookkeeping commit.
