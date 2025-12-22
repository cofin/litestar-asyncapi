# Tasks: PRD-003 Handler Discovery

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Define discovery datastructures
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/datastructures.py`
- **Changes**: Add extractor-facing structures (e.g. `DiscoveredChannel`, `DiscoveredOperation`), or a minimal internal
  representation used by PRD-004.
- **Tests**: `src/tests/unit/extractors/test_datastructures.py`

## Task 2: Create extractor package skeleton
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/__init__.py`
- **Changes**: Add exports and shared helper interfaces.
- **Tests**: N/A

## Task 3: Implement websocket route discovery
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Iterate Litestar routes to find `WebSocketRoute`, extract `path_format`, `path_parameters`, and handler
  metadata required for inference.
- **Tests**: `src/tests/unit/extractors/test_websocket_routes.py`
- **Patterns**: Use `BaseRoute.path_format` and `BaseRoute.path_parameters`.

## Task 4: Implement websocket parameter → AsyncAPI parameter conversion
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Convert `PathParameterDefinition` to AsyncAPI `Parameter` with schema derived from its type.
- **Tests**: `src/tests/unit/extractors/test_websocket_parameters.py`

## Task 5: Implement listener handler inference
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Detect `WebsocketListenerRouteHandler` and extract data + return field definitions for message schemas.
- **Tests**: `src/tests/unit/extractors/test_listener_inference.py`

## Task 6: Implement stream handler inference
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Detect `WebSocketStreamHandler` and extract stream item type for send message schema.
- **Tests**: `src/tests/unit/extractors/test_stream_inference.py`

## Task 7: Implement safe fallback behavior for plain websocket handlers
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Ensure extraction produces a channel even when message schemas cannot be inferred.
- **Tests**: `src/tests/unit/extractors/test_plain_websocket_fallback.py`

## Task 8: Implement ChannelsPlugin extractor
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/channels.py`
- **Changes**: Find ChannelsPlugin, extract known channels and represent them as AsyncAPI channels (best-effort).
- **Tests**: `src/tests/unit/extractors/test_channels_plugin.py`

## Task 9: Add integration test covering multiple handler types
- **Status**: COMPLETE
- **Files**: `src/tests/integration/test_discovery.py`
- **Changes**: Build a Litestar app with websocket handler variants and validate extracted channels/operations.
- **Tests**: This file

---

## Quality Gates

- [x] `make test`
- [x] `make lint`
- [x] 90%+ coverage for extractor modules
