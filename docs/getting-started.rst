===============
Getting Started
===============

The Litestar AsyncAPI plugin provides automatic AsyncAPI 3.0 documentation for Litestar WebSocket handlers.

Installation
============

You can install the plugin using your preferred package manager:

.. code-block:: bash

    # Using pip
    pip install litestar-asyncapi

    # Using uv (recommended)
    uv add litestar-asyncapi

Basic Usage
===========

To enable AsyncAPI documentation, you need to add the ``AsyncAPIPlugin`` to your Litestar application.

.. code-block:: python

    from litestar import Litestar
    from litestar.handlers.websocket_handlers import WebsocketListener
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

    class MyListener(WebsocketListener):
        path = "/events/{topic:str}"

        def on_receive(self, data: dict) -> dict:
            """Echo back the received data."""
            return data

    asyncapi_config = AsyncAPIConfig(
        title="Event API",
        version="1.0.0",
        description="A simple real-time event API",
    )

    app = Litestar(
        route_handlers=[MyListener],
        plugins=[AsyncAPIPlugin(config=asyncapi_config)]
    )

Interactive Documentation
=========================

Once your application is running, you can access the AsyncAPI documentation at the following default paths:

- ``/asyncapi``: AsyncAPI Playground (interactive UI)
- ``/asyncapi.json``: Raw AsyncAPI specification in JSON format
- ``/asyncapi.yaml``: Raw AsyncAPI specification in YAML format

You can customize these paths in the ``AsyncAPIConfig``.

Core Components
===============

Configuration
-------------

The ``AsyncAPIConfig`` class allows you to customize the generated specification. You can provide basic information like ``title``, ``version``, and ``description``, as well as more advanced settings like ``servers``, ``security`` schemes, and custom ``render_plugins``.

Plugin
------

The ``AsyncAPIPlugin`` integrates with Litestar's plugin system to scan your application routes, extract metadata from your WebSocket handlers, and provide the necessary route handlers to serve the documentation.

Renderers
---------

The plugin uses a flexible system of render plugins to serve the documentation. By default, it includes:

- ``AsyncAPIPlaygroundRenderPlugin``: Serves the interactive AsyncAPI Playground.
- ``JsonRenderPlugin``: Serves the raw specification in JSON format.
- ``YamlRenderPlugin``: Serves the raw specification in YAML format.

You can add or remove renderers by providing a list of ``render_plugins`` to the ``AsyncAPIConfig``.

Next Steps
==========

Explore the :doc:`usage/index` guide for more detailed information on how to customize your AsyncAPI documentation, including:

- Documenting channels and operations
- Specifying message schemas
- Using security schemes
- Customizing the UI
