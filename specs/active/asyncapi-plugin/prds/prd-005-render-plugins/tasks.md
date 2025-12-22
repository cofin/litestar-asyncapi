# Tasks: PRD-005 Render Plugins

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**PRD**: `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/prd.md`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Task 1: Implement render plugin base class
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugins.py`
- **Changes**: Add `AsyncAPIRenderPlugin` base with `paths`, `render()`, `render_json()`, `has_path()`, `receive_router()`.
- **Tests**: `src/tests/unit/test_render_plugin_base.py`
- **Patterns**: Mirror `litestar/openapi/plugins.py::OpenAPIRenderPlugin`.

## Task 2: Implement JSON render plugin
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugins.py`
- **Changes**: Add JSON plugin with default `/asyncapi.json`, correct media type, and serializer hook usage.
- **Tests**: `src/tests/unit/test_json_plugin.py`

## Task 3: Implement YAML render plugin
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugins.py`
- **Changes**: Add YAML plugin with default `/asyncapi.yaml` + `/asyncapi.yml`.
- **Tests**: `src/tests/unit/test_yaml_plugin.py`

## Task 4: Implement UI render plugin
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugins.py`
- **Changes**: Add HTML UI plugin embedding AsyncAPI React component via CDN.
- **Tests**: `src/tests/unit/test_ui_plugin.py`

## Task 5: Register docs router in `AsyncAPIPlugin`
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/plugin.py`
- **Changes**: Create docs router and register plugin routes similarly to Litestar OpenAPI.
- **Tests**: `src/tests/integration/test_routes.py`

## Task 6: Export render plugins and constants
- **Status**: COMPLETE
- **Files**: `src/litestar_asyncapi/__init__.py`
- **Changes**: Export render plugin base and built-in plugins.
- **Tests**: N/A

---

## Quality Gates

- [x] `make test`
- [x] `make lint`
- [x] Content types correct in integration tests
