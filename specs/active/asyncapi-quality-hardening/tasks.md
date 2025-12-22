# Tasks: AsyncAPI Quality Hardening

## Task 1: Confirm discovery behavior and constraints
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`, `src/litestar_asyncapi/_asyncapi/extractors/channels.py`
- **Changes**: Document and validate assumptions about route discovery; ensure discovery flow remains best-effort and deterministic.
- **Tests**: Add/expand integration test for nested routers.
- **Patterns**: Discovery pattern from `extract_websocket_channels()`.

## Task 2: Unique operationId generation for ChannelsPlugin
- **Files**: `src/litestar_asyncapi/_asyncapi/extractors/channels.py`
- **Changes**: Generate per-channel operationId values; ensure deterministic naming for arbitrary channels.
- **Tests**: New unit test for ChannelsPlugin with multiple channels.
- **Patterns**: Error handling via `ImproperlyConfiguredException` for invalid config.

## Task 3: Global operationId uniqueness validation
- **Files**: `src/litestar_asyncapi/_asyncapi/generator.py`
- **Changes**: Detect duplicate operationId values; apply deterministic suffix or raise error (decide policy).
- **Tests**: Add unit test for duplicate operationId detection and resolution.
- **Patterns**: Operation key sanitization and reference handling in generator.

## Task 4: Tuple schema generation
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py`, `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
- **Changes**: Implement fixed-length and variadic tuple schema handling with ordered item definitions or min/max items.
- **Tests**: Add schema tests for fixed-length and variadic tuples.
- **Patterns**: Schema generator flow and plugin-based population.

## Task 5: Constraint propagation from FieldDefinition
- **Files**: `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py`, `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
- **Changes**: Map FieldDefinition constraints to Schema fields; ensure type-appropriate application.
- **Tests**: New unit tests for string, number, and array constraints.
- **Patterns**: Utility functions for schema creation in `schema_generation/utils.py`.

## Task 6: Component key normalization and validation
- **Files**: `src/litestar_asyncapi/_asyncapi/datastructures.py`
- **Changes**: Sanitize `schema_component_key` overrides; raise errors for invalid results.
- **Tests**: Add unit tests for valid/invalid component keys and reference output.
- **Patterns**: SchemaRegistry naming and reference tracking.

## Task 7: Parameter schema compliance
- **Files**: `src/litestar_asyncapi/spec/channel.py`, `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
- **Changes**: Limit parameter schema fields to AsyncAPI v3-compliant subset or introduce a restricted parameter schema type.
- **Tests**: Validate parameter schema output for path parameters.
- **Patterns**: Spec object modeling and serialization in `spec/base.py`.

## Task 8: Optional message reference alignment
- **Files**: `src/litestar_asyncapi/_asyncapi/generator.py`, `src/litestar_asyncapi/spec/channel.py`, `src/litestar_asyncapi/spec/operation.py`
- **Changes**: If adopted, generate channel messages and reference them from operations; preserve deterministic message IDs.
- **Tests**: Add integration test verifying message references.
- **Patterns**: Component and reference handling in spec objects.

## Task 9: UI renderer HTML escaping
- **Files**: `src/litestar_asyncapi/plugins.py`
- **Changes**: Escape title and any other interpolated strings using standard library.
- **Tests**: Update UI plugin test for HTML escaping.
- **Patterns**: Render plugin pattern in `plugins.py`.

## Task 10: Nested router discovery test
- **Files**: `src/tests/integration/test_discovery.py`
- **Changes**: Add test ensuring nested routers contribute to `app.routes` discovery for WebSocket channels.
- **Tests**: Integration test only.
- **Patterns**: Integration test pattern in `src/tests/integration/`.

## Task 11: OperationId regression tests
- **Files**: `src/tests/unit/test_generator.py`, `src/tests/unit/extractors/`
- **Changes**: Add tests that assert operationId uniqueness and determinism.
- **Tests**: Unit tests with multiple channels.
- **Patterns**: Function-based pytest tests.

## Task 12: Documentation updates
- **Files**: `README.md` (or release notes if applicable)
- **Changes**: Document new behavior for operationId uniqueness, component key validation, and parameter schema compliance.
- **Tests**: N/A
- **Patterns**: Existing README conventions.
