=================
Litestar AsyncAPI
=================

Automatic AsyncAPI 3.0 document generation and interactive documentation hosting for `Litestar <https://litestar.dev>`_.

.. grid:: 1 2 2 2
    :gutter: 3

    .. grid-item-card:: 🚀 Getting Started
        :link: getting-started
        :link-type: doc

        Install the plugin, register it with your Litestar application, and explore your first generated AsyncAPI specification.

    .. grid-item-card:: 📖 How-to Guides
        :link: usage/index
        :link-type: doc

        Learn how to document WebSocket listeners, streams, configure multi-plugin schema generation, and mount interactive playgrounds.

    .. grid-item-card:: 💡 Examples Gallery
        :link: examples/index
        :link-type: doc

        Explore 6 self-contained, runnable PEP 723 example applications covering listeners, streams, channels, and HTMX.

    .. grid-item-card:: 📚 API Reference
        :link: reference/index
        :link-type: doc

        Browse comprehensive, typed API documentation for plugins, configs, decorators, extractors, and AsyncAPI 3.0 spec objects.

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2
    :caption: Documentation

    getting-started
    usage/index
    examples/index
    reference/index

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 1
    :caption: Development

    contribution-guide
    changelog

Overview
========

``litestar-asyncapi`` introspects your Litestar route handlers, WebSocket connections, and ``ChannelsPlugin`` configurations to automatically generate comprehensive AsyncAPI 3.0 documents.

Key Capabilities
----------------

- **AsyncAPI 3.0 Native**: Complete compliance with the AsyncAPI 3.0 specification hierarchy (info, servers, channels, operations, and components).
- **Automated Route Discovery**: Traverses route trees (including nested routers and controllers) to extract channel paths and operations.
- **Multi-Plugin Type System**: Seamlessly generates JSON Schema schemas from Msgspec structs, Pydantic models (v1 and v2), Attrs classes, Dataclasses, and TypedDict definitions.
- **Interactive Documentation**: Built-in render plugins for AsyncAPI React UI and an interactive WebSocket Playground.
- **Litestar Channels Integration**: Best-effort pub/sub channel discovery when paired with Litestar's ``ChannelsPlugin``.
