---
type: Reference
title: "Contracts & Discovery"
description: Contracts & Discovery reference for the asyncapi-generation skill.
tags: [skills, asyncapi-generation, contracts-and-discovery]
---

# Contracts & Discovery

How typed contracts enter the generator and how routes become `DiscoveredChannel` values.

## Shared contract types

`src/litestar_asyncapi/asyncapi/datastructures.py`

| Type | Role | Invariant |
| --- | --- | --- |
| `MessageDefinition` | Message contract; `payload`/`headers` hold Python types, `FieldDefinition`, `Schema`, `Reference`, `dict`, `bool` or `MultiFormatSchema` | Types stay unrendered until `generator.py::_build_message` |
| `OperationDefinition` | Application-perspective `action` plus named message choices | `__post_init__` coerces `action` to `OperationAction` and rejects duplicate message names |
| `ChannelDefinition` | Explicit channel; `key` is document identity, `address` is transport | Distinct keys may share an address |
| `DiscoveredOperation` / `DiscoveredChannel` | Provenance subclasses (`provenance`, `source`, `route_identity`) | Declare only their own `__slots__` (Python 3.10 inheritance-safe); `kw_only=True` |
| `DiscoverySource` | `WEBSOCKET`, `CHANNELS_PLUGIN`, `CONFIG` | `CONFIG` channels skip operation merging in `_normalize_channels` |

Override semantics: `None` = inherit/infer; explicit value (including `[]`) = override.

## Decorators

`src/litestar_asyncapi/decorators.py`

- `asyncapi_operation` / `asyncapi_message` store `AsyncAPIMetadata.operations[action]` under `route_handler.opt[ASYNCAPI_OPT_KEY]` (`"asyncapi"`), the native handler option layer.
- `_coerce_action` accepts `OperationAction` or case-insensitive `"send"`/`"receive"`; anything else raises `ValueError`.
- `_get_route_handler` raises `ImproperlyConfiguredException` when the decorated object is not a route handler (no `opt`). Decorators apply above `@websocket`.
- Repeated decorators for the same action merge into one `OperationDefinition`; non-`None` arguments win.

## WebSocket extractor

`src/litestar_asyncapi/asyncapi/extractors/websocket.py::extract_websocket_channels`

1. Iterates finalized `app.routes` (`WebSocketRoute` only), so nested router prefixes are already applied.
2. Skips ChannelsPlugin-generated routes (`_compat.py::generated_channels_mode`) and `opt["include_in_schema"] is False` (`_should_include_handler`).
3. Path parameters → `Parameter(description="Path parameter: <name> (type: <T>)")` via `_path_parameters_to_parameters`. No nested schema.
4. `_infer_operations_from_handler`:
   - Listener/stream handlers: `_compat.py::websocket_signature` yields receive/send fields and frame modes. Receive = application receives; send = application sends. A `None` return yields no send operation (`_is_none_return_type`).
   - Each message carries `extensions={"x-websocket-mode": mode}` and `content_type` from `websocket_content_type`.
   - Default `operation_id` is `<handler_name>_<action>`.
   - Raw handlers: no output unless decorated or `config.include_raw_websocket_routes`; then `_infer_raw_websocket_operations` placeholders and a `UserWarning` when any payload remains `None`.
5. Metadata precedence (applied in this order):
   - `_apply_handler_metadata`: handler `summary`/`description` fill blanks; handler `operation_id` overwrites and gains `_<action>` when the handler has more than one operation.
   - `_apply_docstring_descriptions`: only when `config.use_handler_docstrings`; fills blank descriptions via `asyncapi/utils/docstrings.py::get_handler_docstring`.
   - `_apply_decorator_overrides`: decorator non-`None` fields overwrite; decorator `messages` replace inferred messages but inherit inferred `payload`, `content_type` and merge `extensions` (explicit keys win). `replace_placeholders=True` discards raw placeholders.
6. `route_identity=route` binds the channel to the actual route object for merge checks.

## ChannelsPlugin extractor

`src/litestar_asyncapi/asyncapi/extractors/channels.py::extract_channels_plugin_channels`

- Discovers only routes the plugin actually generated (`generated_channels_mode` not `None`). Subscription names without route creation produce nothing.
- Emits one send-only operation with `payload=Schema()` and `text/plain` or `application/octet-stream` by mode.
- User sockets sharing a prefix remain WebSocket-extractor channels.

## Explicit channels

`generator.py::_discover_channels` converts each `AsyncAPIConfig.channels` entry into a `DiscoveredChannel(source=CONFIG, route_identity=None)` with provenance `AsyncAPIConfig.channels[i] (<key>)`, removing inferred channels with the same key. Copy fields through `dataclasses.fields(...)` so new contract fields propagate automatically.

## Canonical tests

| Seam | Test file |
| --- | --- |
| Listener / stream inference | `src/tests/unit/extractors/test_listener_inference.py`, `test_stream_inference.py` |
| Raw sockets | `src/tests/unit/extractors/test_plain_websocket_fallback.py` |
| Decorator overrides | `src/tests/unit/extractors/test_decorator_overrides.py`, `src/tests/unit/test_decorators.py`, `test_decorators_storage.py` |
| Handler metadata / docstrings | `src/tests/unit/extractors/test_handler_metadata.py`, `test_docstring_descriptions.py` |
| Parameters | `src/tests/unit/extractors/test_websocket_parameters.py` |
| ChannelsPlugin | `src/tests/unit/extractors/test_channels_plugin.py` |
| Datastructures | `src/tests/unit/extractors/test_datastructures.py` |
| Nested routers, include_in_schema | `src/tests/integration/test_discovery.py` |
