=======================
Decorator Customization
=======================

When default signature introspection does not provide sufficient detail, ``litestar-asyncapi`` offers explicit decorators to annotate operations and messages.

Operation Overrides
===================

The ``@asyncapi_operation`` decorator customizes operation IDs, summaries, descriptions, and tags.

.. code-block:: python

    from litestar import websocket_listener
    from litestar_asyncapi import asyncapi_operation


    @websocket_listener("/ws/orders")
    @asyncapi_operation(
        operation_id="submitOrder",
        summary="Submit New Order",
        description="Receives client order submissions and dispatches them to the matching engine",
        tags=["Trading", "Orders"],
    )
    async def order_handler(order: dict[str, str]) -> dict[str, str]:
        return {"status": "accepted"}

Message Overrides
=================

The ``@asyncapi_message`` decorator enriches the message payload metadata, specifying titles, summaries, content types, and correlation IDs.

.. code-block:: python

    from litestar import websocket_listener
    from litestar_asyncapi import asyncapi_message


    @websocket_listener("/ws/events")
    @asyncapi_message(
        name="SystemEventMessage",
        title="System Event",
        summary="Broadcast notification of system status changes",
        content_type="application/json",
    )
    async def event_handler(event: dict[str, str]) -> None:
        pass

Combining Decorators
====================

Decorators can be stacked to customize both the operation action and message definitions simultaneously.

.. code-block:: python

    from litestar import websocket_listener
    from litestar_asyncapi import asyncapi_message, asyncapi_operation


    @websocket_listener("/ws/telemetry")
    @asyncapi_operation(
        operation_id="streamTelemetry",
        summary="Stream Device Telemetry",
        tags=["IoT", "Sensors"],
    )
    @asyncapi_message(
        name="TelemetryPayload",
        title="Sensor Telemetry",
        summary="Periodic metrics sample from connected hardware devices",
    )
    async def telemetry_handler(reading: dict[str, float]) -> None:
        pass
