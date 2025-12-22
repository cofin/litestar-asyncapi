## Similar Implementations

1. `src/litestar_asyncapi/_asyncapi/generator.py` - Builds AsyncAPI documents and assembles channels/operations/components.
2. `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` - WebSocket route discovery and operation inference.
3. `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py` - Schema generation from type annotations with plugin hooks.
4. `src/litestar_asyncapi/plugin.py` - InitPluginProtocol integration and docs router registration.
5. `src/tests/unit/test_generator.py` - Baseline generator behavior and channel/operation expectations.

## Patterns Observed

- Class structure: `InitPluginProtocol` plugin with cached config and `on_app_init()` registration.
- Generation flow: `AsyncAPIGenerator` composes discovery -> channels -> operations -> components.
- Schema plugins: pluggable `supports()` + `populate_component_schema()` pattern for model types.
- Error handling: raise `ImproperlyConfiguredException` for invalid user configuration or trait refs.
- Tests: function-based pytest with `pytest.mark.anyio` and inline Litestar app creation.
