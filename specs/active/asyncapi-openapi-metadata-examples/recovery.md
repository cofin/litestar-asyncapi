# Recovery Guide: asyncapi-openapi-metadata-examples

## Session Context
- Complexity: complex
- Checkpoints: 10
- Created: 2025-12-19

## Quick Resume
1. Read this file
2. Read prd.md
3. Check tasks.md for progress
4. Continue from last incomplete task

## Intelligence Context
- Similar features: websocket extractor, schema generation utils, decorator overrides, generator assembly
- Patterns used: dataclass + slots, discovery + override flow, config-driven behavior
- MCP tools needed: Context7 for Litestar docs, WebSearch for AsyncAPI spec

## File Locations
- PRD: specs/active/asyncapi-openapi-metadata-examples/prd.md
- Tasks: specs/active/asyncapi-openapi-metadata-examples/tasks.md
- Research: specs/active/asyncapi-openapi-metadata-examples/research/

## Next Agent
Run: `/implement asyncapi-openapi-metadata-examples`

## Implementation Status
- Status: COMPLETE
- Tasks completed: 12/12
- Coverage: 87%

## Files Changed
- `src/litestar_asyncapi/config.py`: Added docstring/example config flags
- `src/litestar_asyncapi/decorators.py`: Added message examples overrides
- `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`: Metadata/docstring/example extraction
- `src/litestar_asyncapi/_asyncapi/datastructures.py`: Message examples support
- `src/litestar_asyncapi/_asyncapi/utils/docstrings.py`: Docstring extraction helper
- `src/litestar_asyncapi/_asyncapi/utils/examples.py`: Example generation helper
- `src/litestar_asyncapi/_asyncapi/generator.py`: Config passed to websocket extractor
- `src/tests/unit/extractors/test_handler_metadata.py`: Metadata mapping tests
- `src/tests/unit/extractors/test_docstring_descriptions.py`: Docstring extraction tests
- `src/tests/unit/extractors/test_example_generation.py`: Example generation tests
- `src/tests/unit/extractors/test_example_precedence.py`: Example precedence tests
- `src/tests/unit/test_discovered_message.py`: Message examples serialization test
- `src/tests/unit/utils/test_docstrings.py`: Docstring helper tests
- `src/tests/unit/utils/test_examples.py`: Example helper tests
- `src/tests/integration/test_asyncapi_metadata_examples.py`: Full document integration test
- `README.md`: Documented new config options

## Next Agent
Run: `/review asyncapi-openapi-metadata-examples`
