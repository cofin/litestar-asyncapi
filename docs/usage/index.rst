============
Usage Guides
============

Comprehensive guides for configuring and using ``litestar-asyncapi``.

.. grid:: 1 2 2 2
    :gutter: 3

    .. grid-item-card:: Concepts & Architecture
        :link: concepts
        :link-type: doc

        Learn how AsyncAPI 3.0 documents are structured and how Litestar extracts them.

    .. grid-item-card:: WebSocket Handlers
        :link: websocket-handlers
        :link-type: doc

        Document listeners, streams, and raw WebSocket connections.

    .. grid-item-card:: Decorator Customization
        :link: decorators
        :link-type: doc

        Fine-tune operation IDs, summaries, descriptions, and message tags.

    .. grid-item-card:: Schema Generation
        :link: schema-generation
        :link-type: doc

        Configure type inspection for Msgspec, Pydantic, Attrs, and Dataclasses.

    .. grid-item-card:: Channels Plugin
        :link: channels-plugin
        :link-type: doc

        Integrate pub/sub event channels from Litestar ChannelsPlugin.

    .. grid-item-card:: Renderers & Playground
        :link: renderers
        :link-type: doc

        Host interactive UI and the real-time WebSocket Playground.

    .. grid-item-card:: Security & Servers
        :link: security-and-servers
        :link-type: doc

        Define WS/WSS server protocols, hosts, and authentication schemes.

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 1

    quickstart
    concepts
    websocket-handlers
    decorators
    schema-generation
    channels-plugin
    renderers
    security-and-servers
