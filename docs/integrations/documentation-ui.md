# Documentation and interaction

`DocsConfig` sets up the documentation routes, and `render_plugins` replaces them when the defaults do not fit. This application serves Scalar at `/events`, the document at custom JSON and YAML paths, and the React console as a separate page:

```python
--8<-- "docs/examples/renderers.py"
```

## The default routes

`DocsConfig()` mounts, under `/asyncapi`:

- the documentation UI at `/asyncapi/`, using the AsyncAPI React component;
- the document at `/asyncapi/asyncapi.json` as `application/vnd.asyncapi+json`;
- with `yaml=True`, the document at `/asyncapi/asyncapi.yaml` and `/asyncapi/asyncapi.yml` as `application/vnd.asyncapi+yaml`;
- with `interactive=True`, the WebSocket console at `/asyncapi/playground`.

`path`, `guards` and `dependencies` apply to every documentation route, including the packaged assets. `enabled=False` mounts nothing; the document stays available through the plugin and the CLI.

## Choosing a renderer

The default view is the AsyncAPI React component 3.2.1. `DocsConfig(renderer="scalar")` switches to Scalar 1.69.2, which leaves out tuple positions, zero-length bounds and boolean payload schemas, and says so on the page; its agent feature and remote fonts are turned off. Both views read the same downloadable document, and the wheel contains their assets, so no CDN or Node process is needed at runtime.

## Custom renderers

`render_plugins` replaces the default routes. `JsonRenderPlugin`, `YamlRenderPlugin` and `AsyncAPIRenderPlugin` are Litestar's own renderers, so their defaults are OpenAPI paths and media types; pass the AsyncAPI paths and media types yourself, as the example does. A JSON route is added when the list has none, because the UI loads the document from it. Renderer instances are not modified, so set `interactive=True` on an `AsyncAPIUIRenderPlugin` yourself when that page should offer the console. See the [renderers reference](../reference/renderers.md).

## Opt-in WebSocket console

`DocsConfig(interactive=True)` adds the React console at `/playground` under the docs path, and the default React page gains the same controls. A Scalar page links to the console instead; `AsyncAPIUIRenderPlugin(renderer="scalar", interactive=True)` is rejected.

The console uses `asyncapi-ws-plugin` 0.1.0 with URL editing turned off, and never connects on its own. **Its validation is advisory: Send transmits the entered text even when it is malformed or does not match the schema.** The server must validate messages and authorize clients. The console adds no strict mode, validator, transport or header proxy of its own.

Only operations whose messages are JSON text objects or arrays are interactive. That includes nullable roots such as `type: [object, null]` and `oneOf` or `anyOf` unions of objects or arrays. Binary frames, plain text, JSON strings and unconstrained payloads are documented without controls, and one such message, including a reply, makes its whole operation documentation-only. The upstream example sampler does not fill positional tuples reliably, so give tuple payloads explicit examples. Inbound message checks use the upstream classification and are not server-side validation.

To connect, the document must declare a `ws` or `wss` server, and every channel parameter needs a value from its default, first example or first enum entry. Without a server there is no Connect control, and an unresolved value disables it. Browsers cannot attach arbitrary headers such as `Authorization` to a WebSocket, so use query parameters or cookies for socket authentication.

The upstream plugin owns the message logs and shared connections. Collapsing a schema keeps its sockets open; leaving the page closes them. A page restored from the browser's back-forward cache reloads the documentation. A restrictive Content Security Policy is left as configured: if it blocks the scripts, the page still offers the JSON download, and a blocked connection can take the browser's ten-second timeout to fail.
