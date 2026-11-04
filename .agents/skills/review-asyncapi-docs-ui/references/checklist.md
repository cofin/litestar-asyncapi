---
type: Checklist
title: "UI Review Checklist"
description: Review rules for the asyncapi-docs-ui domain.
tags: [skills, review-asyncapi-docs-ui, checklist]
---

# UI Review Checklist

**UI-01 — Every dynamic value interpolated into HTML passes through `html.escape(..., quote=True)`.**
Why: titles, URLs and labels come from application metadata and request routing. Unescaped attributes enable XSS.
Check: f-strings in `render`/`bootstrap_html` add no unescaped `{value}`. `self.favicon`/`self.style` stay native constructor inputs. A hostile case is added to `test_ui_security.py`.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render`, `src/litestar_asyncapi/docs.py::bootstrap_html`

**UI-02 — Inline JSON stays inert: `type="application/json"`, `encode_json`, and `<` replaced by `<`.**
Why: a `</script>` inside options or URLs closes the element and runs markup.
Check: no new `<script>` carries executable inline code. The config is read only through `JSON.parse(textContent)`.
Anchor: `src/litestar_asyncapi/docs.py::bootstrap_html`, `src/litestar_asyncapi/assets/bootstrap.js`

**UI-03 — Browser-side plain messages use `textContent`, never `innerHTML` or string-built DOM.**
Why: status and error text can echo data. Upstream React/Scalar own component rendering.
Check: `bootstrap.js`, `react.ts` and `interactive.ts` add no `innerHTML`, `insertAdjacentHTML` or `dangerouslySetInnerHTML`.
Anchor: `tools/frontend/react.ts::render`, `src/litestar_asyncapi/assets/bootstrap.js`

**UI-04 — The docs router keeps `include_in_schema=False`, `dto=None`, `return_dto=None` and the layered `DocsConfig.guards`/`dependencies`.**
Why: without them, docs leak into OpenAPI, app DTOs rewrite schema bytes, or guards stop covering assets, JSON or the playground.
Check: new handlers are registered on the same router, not on the app. Guards cover every new route (`test_routes.py::test_docs_guards_cover_schema_ui_playground_and_assets`).
Anchor: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.create_docs_router`

**UI-05 — Links and asset URLs come from named routes and `request.url_for`.**
Why: hard-coded `/asyncapi/...` strings break under `DocsConfig.path`, nested routers and an accumulated `root_path`.
Check: names come from `renderer_name`. New links go through `opt["asyncapi_routes"]`.
Anchor: `src/litestar_asyncapi/docs.py::renderer_name`, `docs.py::bootstrap_html`

**UI-06 — `DocsConfig` rejects duplicate renderer names, duplicate normalized paths and `/assets` collisions, and never mutates a caller's `render_plugins` list.**
Why: otherwise a silent route shadowing serves the wrong renderer, or one shared list leaks between configs.
Check: new defaults are appended inside `__post_init__` before the uniqueness loop. A list copy is preserved.
Anchor: `src/litestar_asyncapi/config.py::DocsConfig.__post_init__`

**UI-07 — An `AsyncAPIPlugin` binds to one app and rejects others, whatever the value of `use_cache`.**
Why: one plugin shared by two apps would serve one app's channels and guards in the other's docs.
Check: the ownership check stays ahead of the cache read. `clear_cache` does not reset `_app`.
Anchor: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin._get_document`, `AsyncAPIPlugin.clear_cache`

**UI-08 — Public document accessors return defensive copies, and cached JSON stays immutable bytes.**
Why: a caller mutating a returned dict or `AsyncAPI` object would poison every later response.
Check: `get_asyncapi`/`get_asyncapi_schema` keep `deepcopy`. Renderers receive `get_asyncapi_schema(request.app)`, not the private cache.
Anchor: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.get_asyncapi_schema`

**UI-09 — All renderers share one normalization path through the app's `type_encoders`.**
Why: JSON, YAML, UI and CLI must show the same values, including literal nulls and custom-encoded examples.
Check: no renderer re-serializes with a different serializer or default encoders (`test_json_plugin.py::test_json_yaml_and_ui_share_app_encoder_normalization`).
Anchor: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin._get_document`

**UI-10 — Native renderer behavior is reused, not copied.**
Why: local JSON/YAML renderers, routers, static servers or URL resolvers drift from Litestar and duplicate maintenance.
Check: new renderers subclass or configure `OpenAPIRenderPlugin`/`JsonRenderPlugin`/`YamlRenderPlugin`. No new local YAML dependency detection.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIRenderPlugin`

**UI-11 — Interaction stays opt-in, never auto-connects, keeps `allowUrlEditing: false`, and uses only the upstream ws plugin.**
Why: an automatic or editable connection turns docs into an unrequested client. A second validator or transport contradicts the advisory-validation decision.
Check: `DocsConfig.interactive` defaults to `False`. Scalar still raises on `interactive=True`. No new WebSocket code exists outside `asyncapi-ws-plugin`.
Anchor: `tools/frontend/interactive.ts::interactivePlugin`, `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.__init__`

**UI-12 — Console wire gating covers primary and reply messages and only admits JSON-text object/array payloads.**
Why: binary, mixed or scalar contracts would send frames the server cannot interpret.
Check: `supportsWire` changes keep the reply branch, the `x-websocket-mode` check and the payload type check, with a matching case in `interactive.test.ts`.
Anchor: `tools/frontend/interactive.ts::supportsWire`

**UI-13 — React-view adapters change only the view and keep literal data.**
Why: the upstream parser resolves literal `$ref` and drops own `__proto__` keys. Canonical downloads must stay byte-identical.
Check: the `parseForReact` protect/restore and `reactView` transforms do not run on download routes. A literal-key regression exists in `parse.test.ts`/`view.test.ts`.
Anchor: `tools/frontend/parse.ts::parseForReact`, `tools/frontend/view.ts::reactView`

**UI-14 — Frontend source changes ship with regenerated `assets/ui/**` and still pass the distribution check.**
Why: a stale `manifest.json` or a missing hashed file breaks installed wheels without breaking source tests.
Check: the diff includes the Vite output and `THIRD-PARTY-LICENSES.md` when dependencies change. `make build` runs `tools/frontend/tests/distribution.py`. Entries keep exporting `render`.
Anchor: `vite.config.ts`, `tools/frontend/tests/distribution.py::check_assets`

**UI-15 — Missing-asset and failed-load paths degrade to a readable message and keep the JSON download link.**
Why: CSP, a zip install or a partial deploy must not leave a blank page.
Check: `bootstrap_html` still catches `OSError`/`KeyError`/`ValueError`. `asset_directory` still raises `ImproperlyConfiguredException` for non-filesystem installs. The `static-ui.spec.ts` failure cases still pass.
Anchor: `src/litestar_asyncapi/docs.py::asset_directory`, `docs.py::bootstrap_html`

**UI-16 — Tests use the public seam in canonical files, and focused Python runs use `--no-cov`.**
Why: tests of private shapes lock in implementation details. Focused runs without `--no-cov` exit 1 on the global coverage floor and hide real results.
Check: route tests use `TestClient`/`create_test_client`. Browser behavior lives in `*.spec.ts` against `tools/frontend/tests/server.py`. No new standalone audit-style test files are added.
Anchor: `src/tests/integration/test_routes.py`, `playwright.config.ts`

## Shared schemas and browser fixture paths

Union traversal must distinguish shared sibling references from cycles on the current recursion path. Browser fixture docs paths must satisfy root-path validation, including the Playwright readiness endpoint.
