---
type: Suppressions
title: "Generation False-Positive Suppressions (FP-GEN)"
description: Intentional asyncapi-generation patterns reviewers must not flag.
tags: [skills, review-asyncapi-generation, false-positive-suppressions]
---

# Generation False-Positive Suppressions (FP-GEN)

Intentional repository patterns. A finding matching one of these is suppressed.

## FP-GEN-01 — Internal `operation_id` without a wire field
`OperationDefinition.operation_id` and `DiscoveredOperation.operation_id` exist, but `spec/operation.py::Operation` has no `operationId`. The id seeds the operations-map key in `asyncapi/generator.py::_ensure_unique_operation_id`.
**DO NOT FLAG** the missing wire property or the "unused" returned candidate id; the map key is the identity.

## FP-GEN-02 — Percent-quoting after RFC 6901 escaping
`_json_pointer_escape` applies `urllib.parse.quote(..., safe="~")` after `~0`/`~1` escaping so `{`, `}` and `:` form valid URI-fragment pointers.
**DO NOT FLAG** this as double-escaping; `_validate_references` unquotes before resolution.

## FP-GEN-03 — Provenance subclasses declaring only their own `__slots__`
`asyncapi/datastructures.py::DiscoveredOperation` / `DiscoveredChannel` use `@dataclass(kw_only=True)` with explicit `__slots__` for new fields instead of `slots=True`.
**DO NOT FLAG** as a slots leak or inconsistency; this avoids inherited-field duplication on Python 3.10 and passes `slotscheck`.

## FP-GEN-04 — `BaseSchemaObject` uses `@dataclass` with `__slots__ = ()`
`spec/base.py::BaseSchemaObject` is an empty-slot base so subclasses can be `@dataclass(slots=True)`.
**DO NOT FLAG** the missing `slots=True` on the base.

## FP-GEN-05 — Binding classes excluded from slotscheck
`pyproject.toml` `[tool.slotscheck] exclude-classes` covers `litestar_asyncapi.spec.bindings.*:*Binding`.
**DO NOT FLAG** the exclusion as unjustified; it is configured repository policy for protocol binding models.

## FP-GEN-06 — ChannelsPlugin channels emit an unconstrained `Schema()` payload
`asyncapi/extractors/channels.py::extract_channels_plugin_channels` cannot know broker payload types; it records only frame mode and send direction.
**DO NOT FLAG** the empty schema as a missing contract; explicit `ChannelDefinition` entries document broker payloads.

## FP-GEN-07 — Raw-socket placeholders with `UserWarning`
With `include_raw_websocket_routes=True`, `_infer_raw_websocket_operations` emits `RawMessage`/`RawResponse` with no payload and a warning.
**DO NOT FLAG** the unconstrained message or the warning; it is the documented opt-in for uncertain contracts.

## FP-GEN-08 — Broad `except Exception` in CLI export
`cli.py::register_commands.export` converts any failure into `click.ClickException("AsyncAPI export failed: ...")` chained with `from exc`.
**DO NOT FLAG** as swallowed errors; this is the CLI user-facing boundary and the cause is preserved.

## FP-GEN-09 — Local imports inside extractor functions
`extractors/websocket.py` imports `ASYNCAPI_OPT_KEY`, `AsyncAPIMetadata`, `AsyncAPIConfig` and `get_handler_docstring` inside functions.
**DO NOT FLAG** as style drift; these break import cycles between the package root, config, decorators and extractors.

## FP-GEN-10 — `# type: ignore[return-value]` in `decorators.py::_get_route_handler`
A narrow typed ignore is required to return the duck-typed handler as `BaseRouteHandler`.
**DO NOT FLAG** under the no-inline-comments rule; type-checker pragmas are not explanatory comments.
