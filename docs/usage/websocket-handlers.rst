==================
WebSocket Handlers
==================

Litestar provides three primary paradigms for WebSocket handling. ``litestar-asyncapi`` automatically inspects each handler style to generate channel addresses, parameters, and operation messages.

WebSocket Listeners
===================

The ``@websocket_listener`` decorator creates a high-level handler that receives deserialized data and optionally returns a response message.

.. code-block:: python

    from dataclasses import dataclass
    from litestar import websocket_listener


    @dataclass
    class PingPayload:
        sequence: int


    @dataclass
    class PongPayload:
        sequence: int
        acknowledged: bool


    @websocket_listener("/ws/ping")
    async def ping_handler(data: PingPayload) -> PongPayload:
        return PongPayload(sequence=data.sequence, acknowledged=True)

In this example, the extractor generates:
- Channel: ``/ws/ping``
- Send Operation: Accepts ``PingPayload`` schema from client.
- Receive Operation: Emits ``PongPayload`` schema to client.

WebSocket Streams
=================

The ``@websocket_stream`` decorator defines a handler returning an asynchronous generator or stream of messages.

.. code-block:: python

    from collections.abc import AsyncGenerator
    from dataclasses import dataclass
    from litestar import websocket_stream


    @dataclass
    class PriceUpdate:
        symbol: str
        price: float


    @websocket_stream("/ws/prices/{symbol:str}")
    async def price_stream(symbol: str) -> AsyncGenerator[PriceUpdate, None]:
        while True:
            yield PriceUpdate(symbol=symbol, price=100.0)

For streams, the extractor documents:
- Channel: ``/ws/prices/{symbol}`` with a typed string path parameter ``symbol``.
- Receive Operation: Emits a continuous sequence of ``PriceUpdate`` messages.

Raw WebSocket Handlers
======================

Low-level ``@websocket`` handlers take a ``WebSocket`` connection object directly. Because raw handlers perform manual socket reads and writes, you can use AsyncAPI decorators to supply explicit schema metadata:

.. code-block:: python

    from litestar import WebSocket, websocket
    from litestar_asyncapi import asyncapi_operation


    @websocket("/ws/raw")
    @asyncapi_operation(
        summary="Raw WebSocket Tunnel",
        description="Handles raw binary and JSON frames over WebSocket",
    )
    async def raw_handler(socket: WebSocket) -> None:
        await socket.accept()
        data = await socket.receive_text()
        await socket.send_text(f"echo: {data}")
        await socket.close()

Excluding Handlers from Documentation
=====================================

To exclude specific handlers or routers from the generated AsyncAPI specification, set ``include_in_schema=False`` on the route handler or parent router:

.. code-block:: python

    from litestar import websocket_listener


    @websocket_listener("/ws/internal", include_in_schema=False)
    async def internal_handler(data: str) -> str:
        return data
