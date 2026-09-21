Documentation and interaction
=============================

``DocsConfig`` owns ``path``, ``enabled``, ``guards``, ``dependencies``,
``renderer``, ``interactive``, ``yaml`` and optional ``render_plugins``.
AsyncAPI React component 3.2.1 (React 18.3.1) is the default. Scalar 1.69.2 is selectable with
``DocsConfig(renderer="scalar")``; it omits tuple positions, zero-length bounds
and boolean payload schemas, and its page displays that limitation. Its Agent
and remote fonts are disabled. Both views consume the same downloadable document.
Packaged assets need no CDN or Node server at runtime.

``JsonRenderPlugin``, ``YamlRenderPlugin`` and ``AsyncAPIRenderPlugin`` are direct
exports of Litestar's native renderers/base. Their own defaults remain OpenAPI
paths (``/openapi.json``, ``/openapi.yaml`` and ``/openapi.yml``) and native JSON/YAML
media types. ``DocsConfig`` configures AsyncAPI paths and vendor media types for
you. When constructing them manually, configure those values explicitly:

.. literalinclude:: ../examples/renderers.py
   :language: python

The UI adapter inherits the native unslotted renderer base. Its narrowly scoped
slots-check exception avoids maintaining a duplicate base implementation.
Supplied renderer objects retain their settings and are not mutated by another
``DocsConfig``. With custom renderers, set ``interactive=True`` on a React UI
instance explicitly if interaction is wanted on that instance.

Opt-in WebSocket console
------------------------

``DocsConfig(interactive=True)`` adds the named React console at ``/playground``
under the docs path. The default React page also gains interaction; Scalar links
to the console. ``AsyncAPIUIRenderPlugin(renderer="scalar", interactive=True)``
is rejected because Scalar does not provide this interaction.

The console uses ``asyncapi-ws-plugin`` 0.1.0 with URL editing disabled. It never
auto-connects. **Validation is advisory: Send transmits entered text even when
malformed or schema-invalid.** The server must enforce validation and authorization.
There is no custom strict mode, validator, transport, sampler or header proxy.

Only verified JSON text object/array contracts expose interaction. Binary frames,
plain text, JSON-string roots and unconstrained/ambiguous roots are documented but
not interactive. One unsupported message, including a reply choice, disables
interaction for the whole operation. Supply explicit tuple examples: the upstream
sampler does not reliably seed positional tuples. Inbound logs use upstream
classification and diagnostics; they are not server-side validation evidence.

Explicit ws/wss servers and parameter values are required. Parameters can provide
a default, first example or first enum value. Missing servers expose no connection
control; unresolved values disable Connect. Browser tests exercised real ws frames,
query authentication and WSS URL resolution; they did not establish a live TLS
connection. Browsers cannot attach arbitrary authorization headers to WebSockets.

The upstream plugin owns bounded logs and shared connections. Collapsing schema
details leaves shared send/receive sockets open. Full renderer/plugin unmount and
page departure dispose sockets. A persisted browser back/forward restoration reloads
the documentation. Connection errors preserve downloads; successful reconnection
clears the current alert. Restrictive CSP is not relaxed automatically: script
failures retain a readable fallback, and blocked connections can take the native
10-second connection timeout to report failure.
