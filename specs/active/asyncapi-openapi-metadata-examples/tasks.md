## Task 1: Confirm metadata sources on websocket handlers
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` (read), Litestar docs (research)
- **Changes**: Identified OpenAPI schema generation kwargs (summary/description/operation_id) and documented defensive attribute access approach
- **Tests**: None (research task)
- **Patterns**: Defensive attribute access, avoid private APIs

## Task 2: Add config fields for docstrings and examples
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/config.py`, `src/tests/unit/test_config.py`
- **Changes**: Added `use_handler_docstrings`, `create_examples`, `random_seed` with defaults and docs; updated config defaults test
- **Tests**: `src/tests/unit/test_config.py::test_config_defaults`
- **Patterns**: Config dataclass pattern, PEP 604 types

## Task 3: Add docstring extraction utility
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/utils/docstrings.py`, `src/litestar_asyncapi/_asyncapi/utils/__init__.py`, `src/tests/unit/utils/test_docstrings.py`
- **Changes**: Added normalized docstring helper and tests for handler/docstring cases
- **Tests**: `src/tests/unit/utils/test_docstrings.py`
- **Patterns**: Pure function, no side effects

## Task 4: Map handler metadata in extractor
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`, `src/tests/unit/extractors/test_handler_metadata.py`
- **Changes**: Added handler metadata extraction from attributes/opt and applied to operations; tests for listener/stream metadata
- **Tests**: `src/tests/unit/extractors/test_handler_metadata.py`
- **Patterns**: Discovery + override flow

## Task 5: Apply docstring-derived descriptions
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`, `src/litestar_asyncapi/_asyncapi/utils/docstrings.py`, `src/tests/unit/extractors/test_docstring_descriptions.py`
- **Changes**: Added docstring application controlled by config; improved handler docstring resolution; tests for docstring behavior and decorator precedence
- **Tests**: `src/tests/unit/extractors/test_docstring_descriptions.py`
- **Patterns**: Precedence rules documented in PRD

## Task 6: Extend DiscoveredMessage to support examples
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/datastructures.py`, `src/tests/unit/test_discovered_message.py`
- **Changes**: Added `examples` field to DiscoveredMessage and serialize to Message
- **Tests**: `src/tests/unit/test_discovered_message.py`
- **Patterns**: Dataclass + slots

## Task 7: Implement example generation helper
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/utils/examples.py`, `src/tests/unit/utils/test_examples.py`
- **Changes**: Implemented example generation using FieldDefinition defaults and Polyfactory-backed factories with normalization
- **Tests**: `src/tests/unit/utils/test_examples.py`
- **Patterns**: Schema generation utilities pattern

## Task 8: Integrate example generation into extractor or generator
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`, `src/tests/unit/extractors/test_example_generation.py`
- **Changes**: Generate examples for listener/stream payloads when enabled and attach to DiscoveredMessage
- **Tests**: `src/tests/unit/extractors/test_example_generation.py`
- **Patterns**: Avoid overwrite of explicit examples

## Task 9: Add precedence and override tests
- **Status**: COMPLETE
- **Files**: `src/tests/unit/extractors/test_example_precedence.py`
- **Changes**: Added precedence test ensuring decorator examples override generated examples
- **Tests**: `src/tests/unit/extractors/test_example_precedence.py`
- **Patterns**: Function-based pytest tests

## Task 10: Add integration test for full schema output
- **Status**: COMPLETE
- **Files**: `src/tests/integration/test_asyncapi_metadata_examples.py`
- **Changes**: Added integration test validating docstrings and examples in generated AsyncAPI document
- **Tests**: `src/tests/integration/test_asyncapi_metadata_examples.py`
- **Patterns**: Anyio marker, schema assertions

## Task 11: Update documentation and examples (if required)
- **Status**: COMPLETE
- **Files**: `README.md`
- **Changes**: Documented new AsyncAPIConfig options for docstrings and example generation
- **Tests**: None
- **Patterns**: Clear usage docs, avoid implementation details

## Task 12: Final validation and lint/test
- **Status**: COMPLETE
- **Files**: N/A
- **Changes**: Ran `make lint` and `make test` after final updates
- **Tests**: `make test`, `make lint`
- **Patterns**: Quality gate compliance
