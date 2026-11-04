# Renderers

```python
from litestar_asyncapi import AsyncAPIRenderPlugin, AsyncAPIUIRenderPlugin, JsonRenderPlugin, YamlRenderPlugin
```

Render plugins serve the document under `DocsConfig.path`. Pass them in `DocsConfig.render_plugins` to replace the default UI and JSON routes.

## Documentation UI

::: litestar_asyncapi.AsyncAPIUIRenderPlugin
    options:
      members: false

## Document renderers

`JsonRenderPlugin` and `YamlRenderPlugin` are Litestar's [OpenAPI render plugins](https://docs.litestar.dev/latest/reference/openapi/plugins.html) of the same names, re-exported unchanged. They serve the canonical document as `application/vnd.asyncapi+json` and `application/vnd.asyncapi+yaml` in the default configuration.

`AsyncAPIRenderPlugin` is Litestar's [OpenAPIRenderPlugin][litestar.openapi.plugins.OpenAPIRenderPlugin]. Subclass it and implement `render` to serve the document in another form; the `openapi_schema` argument receives the AsyncAPI document.
