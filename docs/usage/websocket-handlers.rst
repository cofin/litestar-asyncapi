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
No SSE or arbitrary broker-consumer inference is implemented.
