---
type: Suppressions
title: "UI False-Positive Suppressions"
description: Intentional asyncapi-docs-ui patterns reviewers must not flag.
tags: [skills, review-asyncapi-docs-ui, false-positive-suppressions]
---

# UI False-Positive Suppressions

**FP-UI-01 — `AsyncAPIUIRenderPlugin` is excluded from slotscheck.**
DO NOT FLAG: it inherits Litestar's unslotted `OpenAPIRenderPlugin`. Duplicating the native base to satisfy slotscheck would break native reuse. The exclusion in `pyproject.toml [tool.slotscheck] exclude-classes` is deliberate and narrow.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin`

**FP-UI-02 — The interactive console sends schema-invalid or malformed text.**
DO NOT FLAG: validation is advisory by design. The page shows a notice saying so, and the server stays the authority on payloads and authorization. Reports asking for blocking validation or a second validator contradict the accepted decision.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render`, `tools/frontend/tests/interactive.spec.ts`

**FP-UI-03 — Scalar omits tuple positions, zero bounds and boolean payload schemas, and refuses `interactive=True`.**
DO NOT FLAG: these are known upstream limits. Scalar stays opt-in with a visible `role="note"` limitation notice and links to the shared React console. React is the default.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.__init__`

**FP-UI-04 — Docs mounted under an arbitrary ASGI mount produce links without the stripped prefix.**
DO NOT FLAG: Litestar does not accumulate `root_path` for arbitrary ASGI mounts. Native `Router` nesting and a correctly accumulated `root_path` work. The limitation is documented on purpose, not replaced with a second URL resolver.
Anchor: `src/tests/integration/test_routes.py::test_docs_under_asgi_mount_with_accumulated_root_path`

**FP-UI-05 — Hashed bundles, `manifest.json` and `THIRD-PARTY-LICENSES.md` under `src/litestar_asyncapi/assets/ui/` are committed generated files.**
DO NOT FLAG as checked-in build output, minified code or a large diff. Wheels must ship them so consumers need no Node or CDN. Review the source in `tools/frontend/` and check only that the output was regenerated.
Anchor: `vite.config.ts`, `pyproject.toml` hatch `artifacts`

**FP-UI-06 — `self.favicon` and `self.style` are interpolated without `html.escape`.**
DO NOT FLAG: they are native `OpenAPIRenderPlugin` constructor inputs that hold developer-supplied markup (`favicon` defaults to `""`). They never carry document or request data. Flag only if document or request values start flowing into them.
Anchor: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render`

**FP-UI-07 — Zip-import installations raise `ImproperlyConfiguredException`.**
DO NOT FLAG: static routing needs stable filesystem paths, and an extracted temporary directory cannot safely back the router. Unsupported zip imports are an explicit contract.
Anchor: `src/litestar_asyncapi/docs.py::asset_directory`

**FP-UI-08 — `parseForReact` renames `$ref`/`__proto__` keys before parsing, then restores them.**
DO NOT FLAG as tampering with the document: it is a disposable, reversible protection pass against verified upstream parser defects. It applies only to the React view. Canonical downloads are unchanged.
Anchor: `tools/frontend/parse.ts::parseForReact`

**FP-UI-09 — `.json`/`.yaml`/`.yml` misses raise `NotFoundException`, while other unknown docs paths return a static HTML 404.**
DO NOT FLAG as inconsistent: machine clients get Litestar's native error, and browsers get a readable page.
Anchor: `src/litestar_asyncapi/plugins/core.py::_handle_docs_path_not_found`

**FP-UI-10 — `bootstrap.js` is handwritten JavaScript and is not in the Vite build.**
DO NOT FLAG as unbundled or untyped source: it is the stable, CSP-friendly external loader. It reads inert config and dynamically imports the hashed entry from the manifest.
Anchor: `src/litestar_asyncapi/assets/bootstrap.js`
