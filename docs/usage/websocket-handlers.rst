WebSocket handlers
==================

Listeners use Litestar's parameter named ``data``. Its annotation describes
incoming messages (``receive``); the return annotation describes outgoing
messages (``send``). Native DTO transfer schemas and application serializers are
respected. See the :ref:`websocket-listener` example.

Streams produce outgoing ``send`` messages. Native streams send strings as text,
bytes as binary, and other supported values as JSON. Logical schema and frame
carrier are distinct; ``x-websocket-mode`` is this library's extension, not a
standard WebSocket binding field. See :ref:`websocket-stream`.

Raw sockets manually choose how to read and write. Supply explicit decorators,
payloads, content types and descriptions as in :ref:`decorator-overrides`.
Undecorated raw handlers are omitted unless
``include_raw_websocket_routes=True``; opting in documents uncertainty with an
unconstrained payload and warning.

A handler's own ``summary``, ``description`` and ``operation_id``, and its
docstring when ``use_handler_docstrings=True``, fill only the operation fields
that decorators leave empty. This includes operations a decorator adds, such as
the explicit operations of a raw socket.

Each discovered WebSocket channel carries ``x-litestar-source: websocket`` and a
``ws`` channel binding, so client generators can tell native sockets apart from
ChannelsPlugin routes without guessing from the path.

Native ``include_in_schema=False`` on a handler or parent layer excludes it.
No arbitrary broker-consumer inference is implemented.

Server-Sent Events
------------------

HTTP handlers that return ``ServerSentEvent`` are documented as channels with
one ``send`` operation. Their messages use ``contentType: text/event-stream``,
the channel carries an ``http`` binding and ``x-litestar-source: sse``.
``ServerSentEvent`` does not carry an item type, so declare the payload with a
decorator; without one the payload is unconstrained:

.. code-block:: python

   from litestar import get
   from litestar.response import ServerSentEvent

   from litestar_asyncapi import asyncapi_message


   @asyncapi_message(action="send", payload=Price, name="price")
   @get("/prices/{symbol:str}")
   async def prices(symbol: str) -> ServerSentEvent:
       return ServerSentEvent(price_updates(symbol))

Only AsyncAPI decorators describe the channel; the handler's HTTP ``summary``,
``description`` and ``operation_id`` stay in the OpenAPI document. A ``receive``
declaration raises ``ImproperlyConfiguredException``. The channel key is the
route path. When a WebSocket route shares the path, the key becomes
``{path}:sse``; when several methods stream events from one path, each gets
``{path}:sse:{method}``. The address stays the path. ``include_in_schema=False``
hides a handler, and ``AsyncAPIConfig(include_sse_routes=False)`` turns the
discovery off.
