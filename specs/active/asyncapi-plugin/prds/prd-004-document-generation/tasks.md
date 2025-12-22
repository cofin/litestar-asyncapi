# Tasks: PRD-004 Document Generation

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Implement generator orchestration class
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/generator.py`
- **Changes**: Add `AsyncAPIGenerator` that builds an AsyncAPI root object from config + app.
- **Tests**: `src/tests/unit/test_generator.py`
- **Patterns**: Mirror `litestar/_openapi/plugin.py::_build_openapi()` flow.

## Task 2: Wire schema registry to components
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/generator.py`
- **Changes**: Ensure schema registry output is applied to `components.schemas` (and any other sections used).
- **Tests**: `src/tests/unit/test_generator_components.py`

## Task 3: Add integration test for full document generation
- **Status**: COMPLETE
- **Files**: `src/tests/integration/test_full_generation.py`
- **Changes**: Build a Litestar app with websocket handlers, generate document schema dict, and assert structure.
- **Tests**: This file

## Task 4: Extend `AsyncAPIConfig` to support generation settings
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/config.py`
- **Changes**: Add config fields required by generator (defaultContentType, server defaults, discovery toggles).
- **Tests**: `src/tests/unit/test_config.py`

## Task 5: Extend `AsyncAPIPlugin` to provide cached schema
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugin.py`
- **Changes**: Add lazy build + cached `provide_asyncapi()` / `provide_asyncapi_schema()` methods (names TBD).
- **Tests**: `src/tests/integration/test_plugin_cache.py`

---

## Quality Gates

- [x] `make test`
- [x] `make lint`
- [x] 90%+ coverage for document generation modules
