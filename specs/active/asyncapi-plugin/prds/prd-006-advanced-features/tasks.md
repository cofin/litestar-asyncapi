# Tasks: PRD-006 Advanced Features

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Define decorator API and metadata model
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/decorators.py`
- **Changes**: Add decorators for operation/message metadata and define internal metadata structures.
- **Tests**: `src/tests/unit/test_decorators.py`

## Task 2: Store metadata on handlers via `opt`
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/decorators.py`
- **Changes**: Ensure metadata attaches to route handlers (prefer `opt["asyncapi"]`).
- **Tests**: `src/tests/unit/test_decorators_storage.py`

## Task 3: Update websocket extractor to apply override policy
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Read decorator metadata, override inferred message schemas and operation fields.
- **Tests**: `src/tests/unit/extractors/test_decorator_overrides.py`

## Task 4: Add trait support in spec + generator
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/operation.py`, `src/litestar_asyncapi/spec/message.py`, `src/litestar_asyncapi/_asyncapi/generator.py`
- **Changes**: Support defining and reusing operation/message traits and reference them from operations/messages.
- **Tests**: `src/tests/unit/test_traits.py`

## Task 5: Add optional binding objects (Kafka/AMQP)
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/spec/bindings/kafka.py`, `src/litestar_asyncapi/spec/bindings/amqp.py`
- **Changes**: Add binding object models behind feature flags; no requirement to integrate immediately.
- **Tests**: `src/tests/unit/spec/test_optional_bindings.py`

## Task 6: Add integration test for decorator-only websocket handler
- **Status**: COMPLETE
- **Files**: `src/tests/integration/test_decorator_driven.py`
- **Changes**: Plain websocket handler with decorators produces channel + send/receive operations.
- **Tests**: This file

---

## Quality Gates

- [x] `make test`
- [x] `make lint`
- [x] Overrides take precedence over inference
