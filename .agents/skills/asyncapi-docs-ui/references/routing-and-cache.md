---
type: Reference
title: "Routing, Configuration & Cache Ownership"
description: Routing, Configuration & Cache Ownership reference for the asyncapi-docs-ui skill.
tags: [skills, asyncapi-docs-ui, routing-and-cache]
---

# Routing, Configuration & Cache Ownership

## Router assembly — `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.create_docs_router`

1. `Router(config.docs.path, include_in_schema=False, dto=None, return_dto=None, guards=list(docs.guards), dependencies=docs.dependencies)`. The docs routes never appear in OpenAPI and never inherit app DTOs.
2. The route-name map starts as `{"assets": "asyncapi:assets"}` and adds one key per renderer: the `asyncapi:` prefix is stripped, and the key `AsyncAPIUIRenderPlugin` becomes `ui`.
3. `create_static_files_router("/assets", directories=[asset_directory()], name="asyncapi:assets")` serves `bootstrap.js` and `ui/**`. Guards and dependencies are inherited from the parent router.
4. Each renderer gets a `@get(plugin.paths, name=renderer_name(plugin), opt={"asyncapi_routes": names}, media_type=plugin.media_type, sync_to_thread=False)` handler that calls `plugin.render(request, self.get_asyncapi_schema(request.app))`.
5. `/{path:str}` (plus `/` when no renderer claims root) goes to `_handle_docs_path_not_found`. Paths ending in `.json`, `.yaml` or `.yml` raise `NotFoundException`. Other paths return a static HTML 404.
6. `render_plugin.receive_router(router)` runs last, which is the native hook.

`on_app_init` appends the router only when `DocsConfig.enabled`. `on_cli_init` registers `asyncapi export` through Litestar's CLI group. Export works headless with docs disabled.

## Naming — `src/litestar_asyncapi/docs.py::renderer_name`

| Renderer | Route name |
| --- | --- |
| any plugin with `role == "playground"` | `asyncapi:playground` |
| `JsonRenderPlugin` | `asyncapi:json` |
| `YamlRenderPlugin` | `asyncapi:yaml` |
| other | `asyncapi:<ClassName>` |

`bootstrap_html` reads `request.route_handler.opt["asyncapi_routes"]` and reverses every non-asset name with `request.url_for`. Use that path for any new link. Native URL reversal handles `Router` nesting and an ASGI `root_path` that was accumulated correctly.

## Configuration — `src/litestar_asyncapi/config.py::DocsConfig.__post_init__`

- `render_plugins=None` → `_default_render_plugins(renderer, interactive)`: one UI plugin, plus JSON at `/asyncapi.json` with media type `application/vnd.asyncapi+json`. Interactive mode applies only when `renderer == "asyncapi"`.
- A JSON renderer is always ensured. `yaml=True` adds `/asyncapi.yaml` and `/asyncapi.yml` with media type `application/vnd.asyncapi+yaml`.
- `interactive=True` adds `AsyncAPIUIRenderPlugin(path="/playground", interactive=True, role="playground")` unless a playground already exists.
- Duplicate renderer names, duplicate `normalize_path` paths and `/assets` prefixes raise `ValueError`.
- A caller-supplied `render_plugins` list is copied and never mutated (`test_playground.py::test_shared_renderer_configuration_is_not_mutated`).

## Cache ownership — `AsyncAPIPlugin._get_document`

- The first call binds `_app`. A different app raises `ImproperlyConfiguredException`, whether or not caching is on.
- Generation is lazy: `deepcopy(AsyncAPIGenerator(...).build_asyncapi())`, then `encode_json` with the app's `type_encoders`, then `decode_json`. The three values are stored only when `use_cache`.
- Public accessors return `deepcopy` copies, or immutable `bytes`. Mutating a returned dict cannot change cached JSON (`test_plugin_cache.py::test_public_schema_mutation_cannot_poison_cache`).
- Request `Host` never reaches the document. Servers come only from configuration (`test_request_host_and_nested_document_mutations_do_not_change_cached_json`).

## Canonical tests

| Behavior | Test |
| --- | --- |
| media types, names, duplicates, guards, dependencies, mounts | `src/tests/integration/test_routes.py` |
| lazy generation, ownership, defensive copies | `src/tests/integration/test_plugin_cache.py` |
| JSON/YAML/UI share encoder normalization | `src/tests/unit/test_json_plugin.py` |
| console opt-in, Scalar refusal | `src/tests/unit/plugins/test_playground.py` |
