ChannelsPlugin
==============

Only actual generated WebSocket routes are discovered. Set
``create_ws_route_handlers=True`` to expose them. Their operation is ``send``:
the application publishes messages to subscribers; incoming frames are discarded
by the generated route. Text, bytes and JSON values are possible, so discovery
does not invent a universal object/JSON payload.

With ``create_ws_route_handlers=False``, internal subscriptions produce no phantom
network channels. Dynamic subscriptions are not broker contracts. Deduplication
uses native handler identity so a user socket at another address is not hidden.

The example retains an HTTP publishing route and a separate typed echo listener:

.. literalinclude:: ../examples/channels_plugin/app.py
   :language: python

After starting it, publish with:

.. code-block:: bash

   curl -X POST http://localhost:8000/publish/news -H 'Content-Type: application/json' -d '{"message":"hello"}'

The generated subscriber's uncertain wire format is documentation-only in the
console. A client can subscribe directly to its generated route. For an external
broker contract use explicit ``ChannelDefinition`` entries, as in
:doc:`security-and-servers`; declaring one does not implement a broker client.
