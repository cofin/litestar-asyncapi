===============
Litestar AsyncAPI
===============

.. toctree::
    :titlesonly:
    :caption: Documentation
    :name: documentation
    :maxdepth: 2

    getting-started
    usage/index
    reference/index

.. toctree::
    :titlesonly:
    :caption: Development
    :name: development
    :maxdepth: 1

    contribution-guide
    changelog

Litestar plugin for AsyncAPI 3.0 documentation
==============================================

The Litestar AsyncAPI plugin enables automatic AsyncAPI 3.0 documentation for your Litestar applications.
It extracts channel, message, and operation metadata from your WebSocket handlers and application configuration,
providing a complete, interactive AsyncAPI specification.

Features
--------

✨ **AsyncAPI 3.0 Native**: Built from the ground up for the latest AsyncAPI specification
🔧 **Automatic Extraction**: Channel and operation metadata discovered from your WebSocket handlers
🚀 **Interactive UI**: Built-in support for AsyncAPI Playground and other renderers
📊 **Schema Generation**: Automatic JSON Schema generation for your message payloads
🎯 **Type Safe**: Full support for msgspec, Pydantic, attrs, and dataclasses
🔐 **Security**: Support for server security schemes and requirements

Installation
------------

.. code-block:: bash

    pip install litestar-asyncapi

Quick Start
-----------

Add AsyncAPI capabilities to your Litestar application by including the plugin:

.. code-block:: python

    from litestar import Litestar, websocket
    from litestar.handlers.websocket_handlers import WebsocketListener
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

    # 1. Define your WebSocket handler
    class MyListener(WebsocketListener):
        path = "/events/{topic:str}"

        def on_receive(self, data: dict) -> dict:
            """Echo back the received data."""
            return data

    # 2. Configure the plugin
    asyncapi_config = AsyncAPIConfig(
        title="My AsyncAPI",
        version="1.0.0",
        description="Real-time event stream",
    )

    # 3. Create the app with the plugin
    app = Litestar(
        route_handlers=[MyListener],
        plugins=[AsyncAPIPlugin(config=asyncapi_config)]
    )

Your application now exposes AsyncAPI documentation at ``/asyncapi``.

Interactive Documentation
-------------------------

The plugin supports multiple ways to view your AsyncAPI specification:

- **JSON/YAML Specification**: Access the raw spec at ``/asyncapi.json`` or ``/asyncapi.yaml``
- **AsyncAPI Playground**: An interactive UI for exploring and testing your AsyncAPI spec
- **Custom Renderers**: Extensible system for adding your own UI plugins

Core Concepts
-------------

**AsyncAPI 3.0**
    The industry standard for documenting event-driven architectures and asynchronous APIs.

**Channels**
    The addressable components where messages are sent or received (e.g., WebSocket paths).

**Operations**
    The actions performed on channels (e.g., ``send`` or ``receive``).

**Messages**
    The data structures exchanged over channels, including headers and payloads.

How It Works
------------

1. **Scan Routes**: The plugin scans your Litestar application for WebSocket route handlers.
2. **Extract Metadata**: It extracts channel paths, parameters, and operation details from handlers and docstrings.
3. **Generate Schemas**: It uses Litestar's type introspection to generate JSON Schemas for message payloads.
4. **Build Spec**: It assembles everything into a valid AsyncAPI 3.0 specification.
5. **Serve Docs**: It provides route handlers to serve the specification and interactive UIs.

Getting Started
---------------

Check out the :doc:`getting-started` guide to learn the basics, or explore the :doc:`usage/index` for deeper topics.

Community
---------

- **Discord**: `Join the Litestar Discord <https://discord.gg/litestar>`_
- **GitHub**: `litestar-org/litestar-asyncapi <https://github.com/litestar-org/litestar-asyncapi>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
