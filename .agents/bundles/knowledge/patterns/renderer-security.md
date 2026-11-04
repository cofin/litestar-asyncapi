---
type: Pattern
title: Renderer Security Patterns
description: Escaping, inert bootstrap JSON and advisory interaction rules for the packaged documentation UI.
tags: [patterns, security, xss, renderers, ui]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: boot
    resource: src/litestar_asyncapi/docs.py::bootstrap_html
    title: Inert bootstrap HTML
  - id: rend
    resource: src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render
    title: UI renderer
  - id: sec
    resource: src/tests/unit/test_ui_security.py
    title: Hostile-input regressions
  - id: browser
    resource: tools/frontend/tests/static-ui.spec.ts
    title: Real-browser hostile metadata acceptance
---

# Renderer Security Patterns

<!-- truth: start -->
- Escape every dynamic HTML attribute with `html.escape(value, quote=True)`.
- Embed bootstrap config as inert JSON from Litestar `encode_json`, with `<` rewritten to `<` so `</script>` cannot close the element.
- Plain DOM status and error messages use `textContent`; upstream React/Scalar own component rendering.
- Canonical schemas load from named JSON routes, never inlined into HTML.
- Interaction is opt-in and advisory: invalid frames may be sent on purpose; the application validates.
- Keep hostile-input regressions in Python and real-browser suites.
<!-- truth: end -->

## Server-side escaping

`bootstrap_html` builds the page shell[^boot]. Attribute values pass through `html.escape(..., quote=True)`; the configuration object is serialized with `encode_json(config).decode("utf-8").replace("<", "\\u003c")` and placed in a non-executing script element. `AsyncAPIUIRenderPlugin.render` merges renderer options after a round trip through the request app's type encoders[^rend].

Anti-pattern: restoring custom playground HTML or a second escaping layer. Reason: upstream components already escape their own output; a second layer double-encodes legitimate content and hides real escaping gaps.

## Browser rendering

The React view protects literal `$ref` data and own `__proto__` keys against verified parser defects through a reversible pass over the public parser result, leaving canonical downloads unchanged. Python regressions cover hostile titles, descriptions and paths[^sec]; browser suites verify hostile metadata, literal `$ref`, `__proto__`, external-network refusal and restrictive CSP fallbacks[^browser].

## Interaction boundary

Primary and reply wire contracts gate JSON-text interaction. The console never auto-connects. Full unmount closes upstream sockets; a shared connection may outlive a collapsed documentation section. Application-side validation and authorization stay authoritative.

[^boot]: `src/litestar_asyncapi/docs.py::bootstrap_html`
[^rend]: `src/litestar_asyncapi/plugins/renderers.py::AsyncAPIUIRenderPlugin.render`
[^sec]: `src/tests/unit/test_ui_security.py`
[^browser]: `tools/frontend/tests/static-ui.spec.ts`
