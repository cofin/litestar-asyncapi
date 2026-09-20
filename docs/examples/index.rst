================
Examples Gallery
================

The repository provides 6 runnable, self-contained example applications demonstrating various features of ``litestar-asyncapi``. Each example is formatted as a PEP 723 inline script and can be run immediately via ``uv run``.

.. grid:: 1 2 2 2
    :gutter: 3

    .. grid-item-card:: WebSocket Listener
        :link: websocket-listener
        :link-type: ref

        Listener-style WebSocket handler with typed request and response payloads.

    .. grid-item-card:: WebSocket Stream
        :link: websocket-stream
        :link-type: ref

        Continuous streaming WebSocket handler returning an asynchronous generator.

    .. grid-item-card:: Decorator Overrides
        :link: decorator-overrides
        :link-type: ref

        Explicit operation and message customization via AsyncAPI decorators.

    .. grid-item-card:: Channels Plugin
        :link: channels-plugin
        :link-type: ref

        Automated pub/sub channel discovery integrated with Litestar ChannelsPlugin.

    .. grid-item-card:: HTMX WebSocket
        :link: htmx-websocket
        :link-type: ref

        WebSocket integration with client-side HTMX partial HTML swapping.

    .. grid-item-card:: Error Handling
        :link: error-handling
        :link-type: ref

        Structured error reporting, validation handling, and error response schemas.

.. _websocket-listener:

WebSocket Listener Example
==========================

Demonstrates a bi-directional listener handler where incoming messages are deserialized into dataclasses and return values are serialized back to the client.

.. code-block:: bash

    uv run docs/examples/websocket_listener/app.py

.. _websocket-stream:

WebSocket Stream Example
========================

Demonstrates an asynchronous generator stream emitting a continuous sequence of event messages to connected clients.

.. code-block:: bash

    uv run docs/examples/websocket_stream/app.py

.. _decorator-overrides:

Decorator Overrides Example
===========================

Demonstrates using ``@asyncapi_operation`` and ``@asyncapi_message`` to enrich generated metadata with custom IDs, summaries, tags, and titles.

.. code-block:: bash

    uv run docs/examples/decorator_overrides/app.py

.. _channels-plugin:

Channels Plugin Example
=======================

Demonstrates best-effort channel extraction from Litestar's ``ChannelsPlugin`` for distributed publish/subscribe messaging.

.. code-block:: bash

    uv run docs/examples/channels_plugin/app.py

.. _htmx-websocket:

HTMX WebSocket Example
======================

Demonstrates serving HTML partials over WebSocket connections to drive real-time client-side UI updates via HTMX.

.. code-block:: bash

    uv run docs/examples/htmx_websocket/app.py

.. _error-handling:

Error Handling Example
======================

Demonstrates capturing connection exceptions and documenting structured error schemas across WebSocket lifecycles.

.. code-block:: bash

    uv run docs/examples/error_handling/app.py
