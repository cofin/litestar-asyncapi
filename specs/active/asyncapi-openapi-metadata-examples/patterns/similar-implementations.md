## Similar Implementations

1. `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` - Discovers websocket routes, derives operations/messages, applies decorator overrides, infers content types.
2. `src/litestar_asyncapi/_asyncapi/datastructures.py` - Defines Discovered* dataclasses and mapping to spec objects (Message/Operation).
3. `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py` - Applies field constraints and defaults onto schemas; handles Literal/Union typing.
4. `src/litestar_asyncapi/decorators.py` - AsyncAPI metadata overrides via `asyncapi_operation` and `asyncapi_message`.
5. `src/litestar_asyncapi/_asyncapi/generator.py` - Converts discovered channels/operations into AsyncAPI spec objects, manages unique IDs.

## Patterns Observed

- **Dataclass + slots**: Most spec and internal objects are `@dataclass(slots=True)` with explicit optional fields.
- **Discovery + override flow**: Base inference from Litestar handlers, then merge decorator overrides from `route_handler.opt[ASYNCAPI_OPT_KEY]`.
- **Schema generation**: Central `AsyncAPISchemaGenerator` builds payload/headers schemas from `FieldDefinition` and applies `KwargDefinition` constraints.
- **Spec serialization**: Spec objects inherit `BaseSchemaObject` and expose `to_schema()` with `extensions` merged last.
- **Config-driven**: AsyncAPIConfig is the primary input surface for document-level settings and components (traits/servers).
- **Testing conventions**: Function-based pytest tests, explicit fixtures in `conftest.py`, and direct schema assertions.
