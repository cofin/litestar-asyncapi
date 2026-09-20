======================
Renderers & Playground
======================

``litestar-asyncapi`` includes a flexible render plugin architecture that supports multiple interactive documentation interfaces and serialization formats.

Built-in Render Plugins
=======================

The library ships with four standard render plugins:

1. **AsyncAPIUIRenderPlugin**: Renders a standalone AsyncAPI React UI documentation view.
2. **PlaygroundRenderPlugin**: Renders an interactive WebSocket playground allowing developers to connect, inspect schemas, and send/receive real-time messages.
3. **JSONRenderPlugin**: Serializes and serves the raw specification at ``/asyncapi/asyncapi.json``.
4. **YAMLRenderPlugin**: Serializes and serves the raw specification at ``/asyncapi/asyncapi.yaml``.

Configuring Renderers
=====================

Render plugins are configured via the ``render_plugins`` list on ``AsyncAPIConfig``:

.. code-block:: python

    from litestar import Litestar
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin
    from litestar_asyncapi.plugins import (
        AsyncAPIUIRenderPlugin,
        JSONRenderPlugin,
        PlaygroundRenderPlugin,
        YAMLRenderPlugin,
    )

    config = AsyncAPIConfig(
        title="Realtime Service",
        render_plugins=[
            PlaygroundRenderPlugin(path="/playground"),
            AsyncAPIUIRenderPlugin(path="/docs"),
            JSONRenderPlugin(path="/spec.json"),
            YAMLRenderPlugin(path="/spec.yaml"),
        ],
    )

    app = Litestar(plugins=[AsyncAPIPlugin(config=config)])

Interactive WebSocket Playground
================================

The WebSocket Playground provides an interactive developer console:

- **Connection Management**: Connect, disconnect, and reconnect to discovered WebSocket channels.
- **Payload Templates**: Auto-generates valid sample JSON payloads based on registered schemas.
- **Message Log**: Visualizes sent and received frames with millisecond timestamps and syntax highlighting.
- **XSS Sanitization**: All rendered strings and message bodies are strictly sanitized to prevent cross-site scripting vulnerabilities.
