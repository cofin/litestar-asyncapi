# Tasks: PRD-001 AsyncAPI Spec Foundation

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Create `spec/` package skeleton
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/__init__.py`
- **Changes**: Create package exports for core spec objects and enums.
- **Tests**: N/A
- **Patterns**: Mirror `litestar/openapi/spec/__init__.py` export style.

## Task 2: Implement base serializer
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/base.py`
- **Changes**: Implement `BaseSchemaObject.to_schema()` + key/value normalization utilities.
- **Tests**: `src/tests/unit/spec/test_base.py`
- **Patterns**: Mirror `litestar/openapi/spec/base.py` normalization behavior.

## Task 3: Implement root + metadata objects
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/asyncapi.py`, `src/litestar_asyncapi/spec/info.py`
- **Changes**: Add `AsyncAPI`, `Info`, `Contact`, `License`, and related metadata structures.
- **Tests**: `src/tests/unit/spec/test_asyncapi.py`, `src/tests/unit/spec/test_info.py`

## Task 4: Implement server objects
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/server.py`
- **Changes**: Add `Server` + `ServerVariable` and server bindings holder.
- **Tests**: `src/tests/unit/spec/test_server.py`

## Task 5: Implement channel + parameter objects
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/channel.py`
- **Changes**: Add `Channel`, `Parameter`, and required supporting objects for PRD-003/004.
- **Tests**: `src/tests/unit/spec/test_channel.py`

## Task 6: Implement operation objects
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/operation.py`, `src/litestar_asyncapi/spec/reply.py`
- **Changes**: Add `Operation`, operation traits (as placeholders), and reply model scaffolding.
- **Tests**: `src/tests/unit/spec/test_operation.py`

## Task 7: Implement message objects
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/message.py`, `src/litestar_asyncapi/spec/correlation_id.py`
- **Changes**: Add `Message`, message traits placeholders, and correlation ID model.
- **Tests**: `src/tests/unit/spec/test_message.py`

## Task 8: Implement schema object
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/schema.py`
- **Changes**: Add JSON Schema draft-07 aligned schema model sufficient for payload/header usage.
- **Tests**: `src/tests/unit/spec/test_schema.py`

## Task 9: Implement components + references + security scaffolding
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/components.py`, `src/litestar_asyncapi/spec/reference.py`, `src/litestar_asyncapi/spec/security_scheme.py`
- **Changes**: Add core reuse container and `$ref` representation.
- **Tests**: `src/tests/unit/spec/test_components.py`

## Task 10: Implement tags + external docs
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/tag.py`, `src/litestar_asyncapi/spec/external_docs.py`
- **Changes**: Add tags + external docs objects (used across server/channel/message).
- **Tests**: Covered by other unit tests (serialization path)

## Task 11: Implement bindings base + websocket binding
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/bindings/__init__.py`, `src/litestar_asyncapi/spec/bindings/base.py`, `src/litestar_asyncapi/spec/bindings/websocket.py`
- **Changes**: Add binding base and websocket binding models, including extension handling.
- **Tests**: `src/tests/unit/spec/test_bindings.py`

---

## Quality Gates (per task group)

- [x] `make test`
- [x] `make lint`
