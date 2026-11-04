---
type: Task
id: discovery-fixes:t01
title: Name listener operations after the user callback
state: completed
priority: P1
verification_strategy: regression_tdd
depends_on: []
files:
  - src/litestar_asyncapi/_compat.py
  - src/litestar_asyncapi/asyncapi/extractors/websocket.py
  - src/litestar_asyncapi/asyncapi/utils/docstrings.py
  - src/litestar_asyncapi/decorators.py
  - docs/changelog.rst
tests:
  - src/tests/integration/test_discovery.py
  - src/tests/integration/test_cli.py
  - src/tests/unit/test_decorators.py
  - src/tests/unit/utils/test_docstrings.py
plan_revision: 3
plan_commit: 305f2cb
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-04T18:08:00Z
last_verified_commit: d516376
verification_evidence: "RED: test_listener_operations_are_named_after_their_callbacks[False/True] raised Duplicate operationId 'ListenerHandler_receive'; test_factory_listener_name_has_no_local_qualifier saw ListenerHandler_* keys. GREEN: make lint 0, make type-check 0, make test 0 (230 passed, 93.84%), make validate-asyncapi 0"
created_at: 2026-11-04T18:00:00Z
updated_at: 2026-11-04T18:08:00Z
commit: d516376
tags: [discovery, naming, listener]
---

# Name listener operations after the user callback

## Objective

Two `@websocket_listener` handlers `chat` and `feed` produce operations `chat_receive` and `feed_receive` regardless of route order, `strict_uniqueness=True` passes, and a listener defined inside a factory function is named `chat_receive`, never a `<locals>` id (audit B2).

## Context

- **Why `regression_tdd`.** The defect is visible in `AsyncAPIGenerator.build_schema()` operation keys: every listener is named after Litestar's `ListenerHandler` wrapper.
- **Fix (Master Decision 5).** Split `_compat.py::websocket_handler_name` into `websocket_handler_callback` (unwrapped user callback) and `websocket_handler_name` (its `__name__`). Use them for operation ids in `extractors/websocket.py::_infer_operations_from_handler`, for docstrings (replacing `asyncapi/utils/docstrings.py::_iter_docstring_candidates`), for WebSocket provenance and for the error text in `decorators.py`. ChannelsPlugin provenance is out of scope.
- **Invariant.** Private Litestar access stays in `_compat.py`.
- **Canonical tests.** `src/tests/integration/test_discovery.py` (naming), `src/tests/integration/test_cli.py` (exported keys).

## Steps

1. **RED.** Add discovery tests for two listeners in both route orders with `strict_uniqueness=True`, and for a factory-built listener.
2. **GREEN.** Split the helper in `_compat.py`; use it in `extractors/websocket.py::_infer_operations_from_handler`, `asyncapi/utils/docstrings.py::get_handler_docstring` and `decorators.py::asyncapi_message`.
3. Update the expected key in `src/tests/integration/test_cli.py`; add the breaking Fixed line to `docs/changelog.rst`.
4. **Verify** with the gates below.

## Verification

- **Initial:** `uv run pytest src/tests/integration/test_discovery.py -q --no-cov` fails on the new tests (`ListenerHandler_receive` keys).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi` exit `0`.

## Acceptance Criteria

- [x] Listener operations are keyed `<callback>_<action>` independent of route order; strict uniqueness passes.
- [x] A factory-defined listener yields `chat_receive`, with no `<locals>` in keys or provenance.
- [x] Docstring lookup uses the unwrapped callback; `_iter_docstring_candidates` is gone.
- [x] The changelog records the operation-key rename as breaking.

## Notes & Discoveries

- [2026-11-04 18:05] `get_handler_docstring` now takes a route handler and reads `websocket_handler_callback`; `unit/utils/test_docstrings.py` was rewritten to use real listener and raw handlers instead of a fake object with an `fn` attribute.
- [2026-11-04 18:05] Total coverage dipped from 93.91% to 93.84% because the fully covered candidate walker was deleted; missed lines were unchanged (91).
- [2026-11-04 18:05] Raw `@websocket` placeholders keep `handler_name`, which is already the user function name.
