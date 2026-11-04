---
type: Task
id: discovery-fixes:t02
title: Apply handler metadata and docstrings after decorator overrides
state: completed
priority: P1
verification_strategy: regression_tdd
depends_on: [t01]
files:
  - src/litestar_asyncapi/asyncapi/extractors/websocket.py
  - docs/changelog.rst
  - docs/usage/websocket-handlers.rst
tests:
  - src/tests/unit/extractors/test_handler_metadata.py
plan_revision: 3
plan_commit: 305f2cb
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:15:00Z
last_verified_commit: 18625a6
verification_evidence: "RED: test_decorator_added_operation_receives_handler_metadata_and_docstring saw keys {'stream', 'stream_receive'}; test_decorator_metadata_wins_over_handler_metadata hit KeyError 'description'. GREEN: make lint 0, make type-check 0, make test 0 (232 passed, 93.90%), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:15:00Z
commit: 18625a6
tags: [discovery, decorators, metadata]
---

# Apply handler metadata and docstrings after decorator overrides

## Objective

Operations added by `asyncapi_operation`/`asyncapi_message` receive the handler's `opt` summary/description and docstring like inferred operations do, while an explicit decorator `operation_id`, summary or description still wins (audit B7, Master Decision 6).

## Context

- **Why `regression_tdd`.** Observable through `AsyncAPIGenerator.build_schema()`: a decorator-added operation lacks summary and description.
- **Fix.** In `extractors/websocket.py::_infer_operations_from_handler`, call `_apply_decorator_overrides` first, then the fill-if-empty pass (`_apply_handler_metadata`, `_apply_docstring_descriptions`). The handler `operation_id` is applied only to operations whose decorator does not set one.
- **Canonical tests.** `src/tests/unit/extractors/test_handler_metadata.py`.

## Steps

1. **RED.** Add tests: a stream handler with `opt` summary/description and a docstring plus a decorator-added receive operation; a decorator `operation_id` beside a handler `operation_id`.
2. **GREEN.** Reorder the passes and guard the handler `operation_id`.
3. Changelog Fixed line; **verify**.

## Verification

- **Initial:** `uv run pytest src/tests/unit/extractors/test_handler_metadata.py -q --no-cov` fails on the new tests.
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Decorator-added operations get handler summary, description and docstring when they set none.
- [x] Decorator `operation_id`, summary and description still win over handler metadata.

## Notes & Discoveries

- [2026-11-04 18:12] The `include_action_suffix` flag was dropped: the handler `operation_id` is suffixed whenever the handler documents more than one operation. This only differs from before when a decorator adds an operation to a stream.
- [2026-11-04 18:12] Raw sockets with explicit operations now receive the handler docstring; `docs/usage/websocket-handlers.rst` said they did not and was updated.
