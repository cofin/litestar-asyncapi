# Patterns Used (Working Notes)

This is a living scratchpad used during implementation to track which patterns were followed and where they came
from. Keep it updated as each sub-PRD is implemented.

## Primary References

- `litestar/_openapi/plugin.py` - caching + docs router construction
- `litestar/openapi/plugins.py` - render plugin base class and JSON/YAML plugins
- `litestar/openapi/spec/base.py` - `BaseSchemaObject.to_schema()` serialization
- `litestar/_openapi/datastructures.py` - schema registry `$ref` strategy
- `litestar/_openapi/schema_generation/schema.py` - schema generation scaffolding

## Notes

- Prefer copying structure/flow over copying code: keep naming consistent with AsyncAPI terms.
- Keep serialization deterministic; avoid dictionary iteration order dependence in generated output.

## Implementation Notes (PRD-001)

- `@dataclass(slots=True)` creates a new class object in Python, which breaks zero-argument `super()` inside methods.
  When a spec object needs to customize `to_schema()` (e.g., to inline extension keys), call
  `BaseSchemaObject.to_schema(self)` directly instead of `super().to_schema()`.

## Implementation Notes (PRD-002)

- Avoid test module name collisions under `src/tests/unit/*` by making the unit test folders packages:
  `src/tests/unit/__init__.py`, `src/tests/unit/spec/__init__.py`, `src/tests/unit/schema_generation/__init__.py`.
- TypedDicts defined in user code under `from __future__ import annotations` store annotations as strings; resolve via
  `typing.get_type_hints(..., include_extras=True)` before detecting `Required`/`NotRequired`.

## Implementation Notes (PRD-003)

- Prefer route-derived websocket discovery via `WebSocketRoute.path_format` and `WebSocketRoute.path_parameters`.
- Typed websocket handler inference uses Litestar's stored parsed fields:
  - listener: `_parsed_data_field` (receive) and `_parsed_return_field` (send)
  - stream: `_parsed_return_field` for stream item type (send)
- When payload types are defined inside a test function, Litestar evaluates annotations via `typing.get_type_hints()`
  using a signature namespace. Pass `signature_namespace={...}` to
  `websocket_listener(...)` / `websocket_stream(...)` to avoid `NameError` for locally defined classes.

## Project Patterns (Optional Dependencies)

- Centralize optional dependency guards in `src/litestar_asyncapi/_typing.py` and re-export via
  `src/litestar_asyncapi/typing.py` (public facade) using `*_INSTALLED` flags and stub shims.
  Feature modules (e.g. schema generation plugins) should not contain scattered `try/except ImportError`; they should
  instead rely on these flags and shims, mirroring patterns in `sqlspec` / `advanced-alchemy`.
