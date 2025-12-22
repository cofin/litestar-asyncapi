## Patterns Used (Deep Dive)

1. `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
   - **Structure**: module-level helper functions (`_infer_*`, `_apply_*`) with narrow responsibilities.
   - **Discovery flow**: infer operations from handler type, then apply decorator overrides.
   - **Schema usage**: `AsyncAPISchemaGenerator.generate_schema(FieldDefinition)` used consistently.
   - **Precedence**: overrides are applied last, never overwritten after `_apply_decorator_overrides()`.

2. `src/litestar_asyncapi/_asyncapi/datastructures.py`
   - **Dataclasses**: `@dataclass(slots=True)` for internal representations.
   - **Mapping**: `DiscoveredMessage.to_spec_message()` converts fields to spec object without side effects.
   - **Error handling**: raises `ImproperlyConfiguredException` for invalid schema key collisions.

3. `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
   - **Helper style**: pure functions, no state; minimal imports; no class usage.
   - **Constraint application**: `apply_field_constraints()` handles reference wrapping and mutable schema updates.
   - **Type handling**: uses `typing.get_origin`/`get_args` and PEP 604 unions via `UnionType`.

4. `src/litestar_asyncapi/decorators.py`
   - **Metadata storage**: stores dataclass-based metadata in `route_handler.opt[ASYNCAPI_OPT_KEY]`.
   - **Validation**: uses simple coercion and raises `ImproperlyConfiguredException` for invalid usage.

5. `src/litestar_asyncapi/_asyncapi/generator.py`
   - **Assembly**: uses discovered channels/operations to build AsyncAPI spec objects.
   - **ID safety**: operation IDs are sanitized and deduplicated with helper functions.

## Conventions to Preserve

- PEP 604 types (`T | None`) and stringified annotations under `TYPE_CHECKING`.
- `@dataclass(slots=True)` for new internal structs.
- Google-style docstrings with `Args`/`Returns` sections.
- No relative imports; use absolute imports.
- Avoid direct access to private Litestar fields unless already used (e.g., `_parsed_data_field`).
