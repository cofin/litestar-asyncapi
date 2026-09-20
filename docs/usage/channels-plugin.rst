===============
Channels Plugin
===============

Litestar provides a built-in ``ChannelsPlugin`` for scalable publish/subscribe messaging across memory, Redis, or Postgres backends. ``litestar-asyncapi`` includes native discovery for ChannelsPlugin configurations.

Automatic Discovery
===================

When both ``ChannelsPlugin`` and ``AsyncAPIPlugin`` are registered on the application, the AsyncAPI generator inspects the channels configuration:

.. code-block:: python

    from litestar import Litestar
    from litestar.channels import ChannelsPlugin
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

    channels_plugin = ChannelsPlugin(
        backend=MemoryChannelsBackend(),
        channels=["notifications", "system.alerts", "chat.{room_id:str}"],
    )

    app = Litestar(
        plugins=[
            channels_plugin,
            AsyncAPIPlugin(config=AsyncAPIConfig(title="PubSub Service")),
        ],
    )

Channel Extraction Behavior
===========================

The ``ChannelsExtractor`` evaluates channel definitions using two approaches:

1. **Route Handlers Enabled (``create_ws_route_handlers=True``)**:
   When Litestar generates WebSocket route handlers for the declared channels, the WebSocket extractor discovers them directly from the route tree, capturing exact path parameters and request decorators.

2. **Internal Channels Mapping (``create_ws_route_handlers=False``)**:
   When explicit WebSocket routes are omitted, the channels extractor maps the declared channels list into AsyncAPI channel entities and receive operations, capturing pub/sub destinations that are published internally.

Deduplication
=============

If a channel is discovered through both a WebSocket route handler and the ChannelsPlugin channel list, ``litestar-asyncapi`` deduplicates the channel address to ensure a singular, unified channel definition in the resulting specification.
