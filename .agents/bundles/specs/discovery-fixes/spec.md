---
type: Spec
flow_id: discovery-fixes
title: Discovery, Naming and Decorators
description: Name listener operations after the user function, apply metadata after decorator overrides, merge decorator messages by name, validate config inputs, and delete discovery code that only synthetic tests reach.
state: draft
parent_prd: contract-fixes
research: []
plan_revision: 2
plan_commit: null
state_revision: 0
current_task: null
last_verified_checkpoint: null
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
tags: [generation, discovery, decorators, debloat]
---

# Discovery, Naming and Decorators

## Charter

Fix how operations and messages are named and assembled from handlers and decorators (audit B2, B7, B8, B12 action and spec_version), and carry out the discovery rows of the Master debloat ledger. Domain skill: `asyncapi-generation`. Review with `review-asyncapi-generation`.

## Upstream Dependencies

- `public-hygiene`.

## Key Deliverables

- **Listener unwrapping.** Split `_compat.py::websocket_handler_name` per Master Decision 5. The split helpers are used in four places:
  - operation ids in `extractors/websocket.py::_infer_operations_from_handler`;
  - docstrings, replacing `asyncapi/utils/docstrings.py::_iter_docstring_candidates`;
  - the existing WebSocket provenance;
  - the error text in `decorators.py`.

  Add a test proving that a listener defined inside a factory function gets `chat_receive`, not a `<locals>` id.
- **B2.** Two listeners `chat` and `feed` yield operations `chat_receive` and `feed_receive`, independent of route order, and `strict_uniqueness=True` passes. Update the expected keys in `src/tests/integration/test_cli.py`.
- **B7.** `_apply_decorator_overrides` runs before the fill-if-empty pass for metadata and docstrings.
- **B8.** `decorators.py` merges messages by name in either stacking order, raises on a conflicting name, and re-validates the `OperationDefinition`.
- **B12.** `OperationDefinition.__post_init__` normalizes `action`, and `_coerce_action` is deleted. `AsyncAPIConfig.__post_init__` rejects an unsupported `spec_version`.
- **Debloat** (the Master ledger rows assigned to chapter 4):
  - First, add an integration-suite assertion that discovery never yields duplicate channel keys.
  - Delete the merge block and the operation-dedupe loop in `_normalize_channels`. Delete two of the three monkeypatched tests and rewrite the conflict test through real routes.
  - Replace the `Reference` guard in `_populate_operations` with a type-safe lookup.
  - Drop the unused `schema_generator` argument.
  - Simplify `_is_none_return_type` and `_should_include_handler`.
  - Replace `unit/extractors/test_websocket_helpers.py` with public-seam cases.
  - Merge `test_decorators_storage.py`, `test_websocket_discovery_alignment.py` and `test_operation_id_hardening.py` into their canonical files.
- **Changelog.** `docs/changelog.rst` records the operation-key rename as a breaking fix.

## Public Seams

- `AsyncAPIGenerator.build_schema`
- `asyncapi_operation`, `asyncapi_message`
- `OperationDefinition`, `AsyncAPIConfig`

## Acceptance Boundary

- Behavior tests exist for B2, B7, B8 and B12.
- Coverage of `asyncapi/generator.py` and `asyncapi/extractors/` is at or above the baseline, and no test monkeypatches an extractor to produce impossible input.
