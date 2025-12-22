# Tasks: PRD-002 AsyncAPI Schema Generation

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Create schema generation package skeleton
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/__init__.py`, `src/litestar_asyncapi/_asyncapi/schema_generation/__init__.py`
- **Changes**: Create packages and minimal exports.
- **Tests**: N/A

## Task 2: Implement AsyncAPI schema registry
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/datastructures.py`
- **Changes**: Implement schema registry with stable keys + `$ref` handling; components schema map generation.
- **Tests**: `src/tests/unit/schema_generation/test_registry.py`
- **Patterns**: Mirror `litestar/_openapi/datastructures.py::SchemaRegistry`.

## Task 3: Implement base schema generator
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py`
- **Changes**: Implement `AsyncAPISchemaGenerator` with TYPE_MAP and `generate_schema()` API.
- **Tests**: `src/tests/unit/schema_generation/test_schema_generation.py`
- **Patterns**: Mirror `litestar/_openapi/schema_generation/schema.py` (structure, not types).

## Task 4: Implement typing + annotation utilities
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
- **Changes**: Helpers for union/optional/literal detection, origin inspection, and safe fallbacks.
- **Tests**: Covered by `src/tests/unit/schema_generation/test_schema_generation.py`

## Task 5: Add plugin interface for model libraries
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/__init__.py`
- **Changes**: Define a small plugin protocol and registration mechanism.
- **Tests**: Covered by unit tests for each plugin module.

## Task 6: Add Pydantic model support
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/pydantic.py`
- **Changes**: Convert Pydantic models to object schemas with properties/required.
- **Tests**: `src/tests/unit/schema_generation/test_pydantic.py`

## Task 6a: Add attrs class support
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/attrs.py`
- **Changes**: Convert attrs classes to object schemas with properties/required.
- **Tests**: `src/tests/unit/schema_generation/test_attrs.py`

## Task 7: Add dataclass support
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/dataclass.py`
- **Changes**: Convert dataclasses to object schemas.
- **Tests**: `src/tests/unit/schema_generation/test_dataclass.py`

## Task 8: Add msgspec Struct support
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/msgspec.py`
- **Changes**: Convert msgspec Struct to object schema; respect field metadata if present.
- **Tests**: `src/tests/unit/schema_generation/test_msgspec.py`

## Task 9: Add TypedDict support
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/typed_dict.py`
- **Changes**: Convert TypedDict to object schema; required/optional keys.
- **Tests**: `src/tests/unit/schema_generation/test_typed_dict.py`

---

## Quality Gates

- [x] `make test`
- [x] `make lint`
