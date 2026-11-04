---
hide:
  - navigation
---

# Litestar AsyncAPI

<div class="lv-home-hero" markdown>
![Litestar AsyncAPI](_static/logo-light.svg){ .lv-hero-banner .lv-hero-banner--light width="320" }
![Litestar AsyncAPI](_static/logo-dark.svg){ .lv-hero-banner .lv-hero-banner--dark width="320" }
</div>

Generate AsyncAPI 3.1 documents from finalized Litestar WebSocket routes, or
supply explicit channel contracts. Serve packaged documentation with optional
WebSocket interaction, or export documents without mounting any docs routes.

The implementation reuses Litestar's schema creator, application encoders,
routers, CLI, and JSON/YAML renderers. Inline schemas use Draft07 tuple semantics.
AsyncAPI 3.0 remains an explicit configuration option.

Start with [Installation](learn/installation.md), then consult the [Learn](learn/index.md)
guides and the [runnable examples](learn/examples.md). Existing users should read the
[migration guide](project/migration.md) before upgrading.
The [documentation UI](integrations/documentation-ui.md) guide records Scalar display limitations and the
optional console's advisory validation behavior.
