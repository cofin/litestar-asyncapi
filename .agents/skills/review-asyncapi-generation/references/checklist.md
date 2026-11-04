---
type: Checklist
title: "Generation Review Checklist (GEN)"
description: Review rules for the asyncapi-generation domain.
tags: [skills, review-asyncapi-generation, checklist]
---

# Generation Review Checklist (GEN)

All paths are relative to `src/litestar_asyncapi/` unless prefixed with `src/tests/`.

## GEN-01 — **Operation identity is the operations-map key; no wire `operationId`.**
- Why: AsyncAPI 3 identifies operations by map key; an `operationId` property is invalid for the pinned schemas.
- Check: No `operation_id` field added to `spec/operation.py::Operation` or emitted via `extensions`.
- Anchor: `asyncapi/generator.py::_populate_operations`

## GEN-02 — **Operation ids and keys are compared with `.casefold()`.**
- Why: Case-insensitive code generators collide on `myOp` / `MYOP`.
- Check: Every uniqueness set stores casefolded values and every lookup casefolds the candidate; `strict_uniqueness` raises `ImproperlyConfiguredException`, else suffixes from `_2`.
- Anchor: `asyncapi/generator.py::_ensure_unique_operation_id`, `_ensure_unique_message_key`

## GEN-03 — **Every generated `$ref` token is RFC 6901 escaped.**
- Why: Parameterized addresses like `/ws/{room_id:str}` contain `/` and break pointers.
- Check: New `Reference(ref=...)` strings wrap each dynamic segment in `_json_pointer_escape`.
- Anchor: `asyncapi/generator.py::_json_pointer_escape`

## GEN-04 — **New reference kinds are validated.**
- Why: `_validate_references` is the only guard against dangling or misplaced refs before serving.
- Check: A new `$ref` position is indexed by `_reference_index` with the correct kind, and a negative test proves a bad target raises.
- Anchor: `asyncapi/generator.py::_reference_index`, `_validate_references`

## GEN-05 — **Conflicts raise with both provenances; nothing is silently overwritten.**
- Why: Users must locate both conflicting declarations.
- Check: New merge logic compares by `_definition_key` and raises `ImproperlyConfiguredException` naming both sources; no `dict.update` over user-supplied components.
- Anchor: `asyncapi/generator.py::_merge_components`, `_normalize_channels`

## GEN-06 — **Ordering and equality use `_definition_key`, never object identity.**
- Why: Output must be byte-stable across runs and processes.
- Check: No `id()`, `hash()` of objects, set iteration order, or `repr` of arbitrary objects in sort keys; `provenance` and `route_identity` stay excluded.
- Anchor: `asyncapi/generator.py::_definition_key`

## GEN-07 — **`None` means "no override"; explicit empty lists override.**
- Why: Users suppress inferred messages/examples with `[]`.
- Check: New code uses `is None` / `is not None`, not truthiness, when deciding inheritance for messages, examples, traits.
- Anchor: `asyncapi/extractors/websocket.py::_apply_decorator_overrides`, `asyncapi/generator.py::_build_message`

## GEN-08 — **New contract fields propagate end-to-end.**
- Why: A field on `MessageDefinition`/`OperationDefinition`/`ChannelDefinition` that is not copied is silently dropped.
- Check: The field reaches decorators, `_apply_decorator_overrides`, `_discover_channels` field copying, `_build_message` / `_populate_operations`, the spec model, and a wire test.
- Anchor: `asyncapi/datastructures.py::MessageDefinition`, `OperationDefinition`, `ChannelDefinition`

## GEN-09 — **Payload types stay unrendered until assembly.**
- Why: Early schema rendering bypasses the shared registry and example precedence.
- Check: Extractors pass Python types / `FieldDefinition` / `NativeDTOPayload`; only `_build_message` calls `schema_generator.generate`.
- Anchor: `asyncapi/generator.py::_build_message`

## GEN-10 — **Discovery honors `include_in_schema` and finalized routes.**
- Why: Hidden handlers must not leak; nested router prefixes come from `app.routes`.
- Check: New extraction iterates `app.routes`, calls `_should_include_handler`, and keeps ChannelsPlugin routes out of the WebSocket extractor via `generated_channels_mode`.
- Anchor: `asyncapi/extractors/websocket.py::extract_websocket_channels`, `extractors/channels.py::extract_channels_plugin_channels`

## GEN-11 — **Raw sockets never fabricate payload contracts.**
- Why: Socket parameters do not describe messages.
- Check: Raw handlers emit operations only when decorated or `include_raw_websocket_routes=True`, and unconstrained output carries the `UserWarning`.
- Anchor: `asyncapi/extractors/websocket.py::_infer_operations_from_handler`, `_infer_raw_websocket_operations`

## GEN-12 — **Action direction is application-perspective.**
- Why: Listener input is `receive`, listener output and streams are `send`; inverting it misleads clients.
- Check: New inference maps receive fields to `OperationAction.RECEIVE` and send/return fields to `SEND`; `None` returns emit no send.
- Anchor: `asyncapi/extractors/websocket.py::_infer_operations_from_handler`

## GEN-13 — **AsyncAPI 3 `Parameter` has no nested schema.**
- Why: The 3.0/3.1 schemas reject `schema` on Parameter.
- Check: Type information goes in `description`; only `description`, `enum`, `default`, `examples`, `location`, `extensions` are set.
- Anchor: `spec/channel.py::Parameter`, `asyncapi/extractors/websocket.py::_path_parameters_to_parameters`

## GEN-14 — **Spec models are slotted `BaseSchemaObject` dataclasses with correct omission.**
- Why: `slotscheck` gates owned classes; wrong omission drops explicit `null` or emits empty keys.
- Check: `@dataclass(slots=True)`; nullable literal fields use `default=UNSET` + `metadata={"nullable": True}`; wire key overrides use `metadata={"alias": "<str>"}`; extensions remain `x-` only.
- Anchor: `spec/base.py::BaseSchemaObject.to_schema`, `_normalize_key`

## GEN-15 — **Logical content type stays separate from frame mode.**
- Why: Text frames may carry non-JSON; mixed streams do not imply JSON.
- Check: `content_type` comes from explicit metadata or `_infer_content_type`; frame mode lives only in `x-websocket-mode`; `default_content_type` stays `None` unless configured.
- Anchor: `asyncapi/generator.py::_infer_content_type`

## GEN-16 — **Private Litestar access and code style stay inside their boundaries.**
- Why: `_compat.py` is the single place to adapt to Litestar changes across `>=2.24.0`.
- Check: No `litestar._*` or private handler attribute access outside `_compat.py`; PEP 604/585 annotations; no inline `#` comments in source (Google docstrings instead); focused tests run with `--no-cov`.
- Anchor: `_compat.py::websocket_signature`, `generated_channels_mode`

## Test evidence

- Behavior tests live in the canonical file for the seam (see `../../asyncapi-generation/references/contracts-and-discovery.md` and `assembly-and-identity.md` test maps).
- Tests build a real `Litestar` app; they do not mock `AsyncAPIGenerator` or extractors.
- Each new raise path has a `pytest.raises(ImproperlyConfiguredException, match=...)` test.

## Server and topic identity checks

When derived root servers exist, omitted and empty channel servers both select them. Require explicit nonempty lists on unrelated channels. Verify fixed ChannelsPlugin topic identity through native callbacks rather than normalized URL prefixes; include relative base paths and slash-bearing topics.
