# Recovery Guide: PRD-003 Handler Discovery

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Quick Resume

1. Read `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md`
2. Use `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/tasks.md` as the checklist
3. Confirm PRD-001 and PRD-002 are stable (spec objects + schema generator)
4. Start with websocket discovery + parameters; add inference; then ChannelsPlugin extraction

---

## Primary References

- `litestar/routes/websocket.py::WebSocketRoute`
- `litestar/routes/base.py::BaseRoute.path_format / path_parameters`
- `litestar/handlers/websocket_handlers/listener.py` (typed `data` / return fields)
- `litestar/handlers/websocket_handlers/stream.py` (typed stream item fields)
- `litestar/channels/plugin.py` (ChannelsPlugin behavior)

---

## Next Step

After PRD-003 is complete, proceed to:
- `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md`

---

## Implementation Status

- Quality gates: `make test` PASS, `make lint` PASS, extractor coverage ≥ 90% PASS
- Core implementation:
  - `src/litestar_asyncapi/_asyncapi/datastructures.py` (discovery datastructures)
  - `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` (WebSocketRoute discovery + inference)
  - `src/litestar_asyncapi/_asyncapi/extractors/channels.py` (ChannelsPlugin discovery, best-effort)
- Tests:
  - `src/tests/unit/extractors/test_datastructures.py`
  - `src/tests/unit/extractors/test_websocket_routes.py`
  - `src/tests/unit/extractors/test_websocket_parameters.py`
  - `src/tests/unit/extractors/test_listener_inference.py`
  - `src/tests/unit/extractors/test_stream_inference.py`
  - `src/tests/unit/extractors/test_plain_websocket_fallback.py`
  - `src/tests/unit/extractors/test_channels_plugin.py`
  - `src/tests/unit/extractors/test_websocket_helpers.py`
  - `src/tests/integration/test_discovery.py`
