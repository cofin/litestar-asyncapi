---
type: Reference
title: "Frontend Bundle, Bootstrap Protocol & Interactive Console"
description: Frontend Bundle, Bootstrap Protocol & Interactive Console reference for the asyncapi-docs-ui skill.
tags: [skills, asyncapi-docs-ui, frontend-and-interaction]
---

# Frontend Bundle, Bootstrap Protocol & Interactive Console

## HTML shell — `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render`

- The title comes from `info.title` when it is a string, otherwise `"AsyncAPI"`. It is always passed through `html.escape(title, quote=True)`.
- `renderer="scalar"` emits a `role="note"` limitation notice: tuple positions, zero-length bounds and boolean payload schemas are omitted. `interactive=True` emits the advisory-validation notice.
- Renderer `config` is normalized through the app's type encoders and then merged with `interactive`.
- The constructor raises `ValueError` for `renderer="scalar", interactive=True`.

## Bootstrap protocol — `src/litestar_asyncapi/docs.py::bootstrap_html` + `assets/bootstrap.js`

1. The server emits `#asyncapi-config` as `type="application/json"` with `{schemaUrl, entry, options, entryUrl}`. The JSON is encoded with `encode_json`, then `<` is replaced by `<`.
2. CSS comes from walking `manifest.json` recursively from `tools/frontend/<entry>.ts` through its `imports`. Any `OSError`, `KeyError` or `ValueError` replaces the styles with a `role="alert"` missing-assets message.
3. The page includes `<nav>` links to every named route, a `#asyncapi-status` live region and `<script src=".../bootstrap.js" defer>`.
4. `bootstrap.js` fetches `schemaUrl` (same-origin credentials) and checks that `asyncapi` is `3.0.0` or `3.1.0` and that `info` exists. It then runs `import(entryUrl)` and calls `render(schema, options)`. If `render` returns a disposer, it runs on `pagehide`. A persisted `pageshow` reloads the page.
5. Failures write a fixed message through `textContent` and set `role="alert"`.

## Vite entries — `vite.config.ts`

- The inputs are `react: tools/frontend/react.ts` and `scalar: tools/frontend/scalar.ts`, written to `src/litestar_asyncapi/assets/ui` with `emptyOutDir`, `manifest.json` and `THIRD-PARTY-LICENSES.md`. `base: './'` keeps imports relative.
- `preserveEntrySignatures: 'strict'` keeps the exported `render` that `bootstrap.js` calls.
- `pyproject.toml` hatch `artifacts = ["src/litestar_asyncapi/assets/**"]` ships the output. `tools/frontend/tests/distribution.py::check_assets` confirms that the wheel and sdist contain every file and every manifest entry.

## React adapter chain — `tools/frontend/react.ts::render`

`parseForReact(schema)` → `<AsyncApi schema config plugins onPluginEvent>`.

- `parse.ts::parseForReact` runs `reactView` first. It then renames literal `$ref`/`__proto__` keys found in data maps or literal positions (`examples`, `example`, `const`, `default`, `enum`) to a collision-free `x-litestar-protected-ref-N` prefix. It calls public `Parser.parse`, then restores the keys in the parser's `document.json()` graph.
- `view.ts::reactView` unwraps compatible Draft07 MultiFormat envelopes, converts boolean schemas into equivalent object schemas, and remaps the affected references. Unknown formats and schema-shaped literal data stay unchanged.
- Plugin events: `ws:status` `open` clears the status region. `PLUGIN_EVENT_ERROR`, `blocked-precheck` and `closed-unexpected` set a fixed `textContent` alert.

## Interactive console — `tools/frontend/interactive.ts`

- `interactivePlugin` wraps `createWsPlugin({ allowUrlEditing: false })` and intercepts `registerComponent` only for `PluginSlot.OPERATION`.
- `supportsWire` requires every primary and reply message to have content type `application/json`, an `x-websocket-mode` of `text` or unset, and a payload of `type` `object` or `array`. Anything else renders a `role="note"` paragraph.
- Connections need an explicit `ws`/`wss` server and resolved parameters. The console never auto-connects. Validation is advisory and sends the exact textarea text.

## Browser and frontend tests

| File | Covers |
| --- | --- |
| `tools/frontend/tests/view.test.ts` | MultiFormat unwrap, boolean translation, literal preservation, binding refs |
| `tools/frontend/tests/parse.test.ts` | literal `$ref`, `__proto__`, alias prefixes, named bindings |
| `tools/frontend/tests/interactive.test.ts` | `supportsWire` gating |
| `tools/frontend/tests/static-ui.spec.ts` | React/Scalar, 3.0/3.1 and mounted routes with external network aborted; fetch/asset/CSP/invalid-document failures |
| `tools/frontend/tests/interactive.spec.ts` | invalid sends, unsupported wires, unresolved params, tuple composer, auth rejection, connect-CSP, secure variables |
| `tools/frontend/tests/server.py` | the Litestar app served on `127.0.0.1:8917` for Playwright |

`playwright.config.ts` writes artifacts to `.tmp/test-results` and starts `server.py`, or `ASYNCAPI_BROWSER_SERVER` for the installed-wheel lane. Normal pages must show zero console errors and zero external requests.
