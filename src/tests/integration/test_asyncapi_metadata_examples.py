from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from litestar import Litestar, websocket_listener
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi._asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import OperationAction, Reference

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_asyncapi_docstrings_and_examples_in_document() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def listener(socket: "WebSocket", data: Payload) -> Payload:
        """Listener docs.

        Raises:
            RuntimeError: Always raised.
        """
        raise RuntimeError

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        """Stream docs.

        Yields:
            Payload: The example payload.
        """
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[listener, stream])
    config = AsyncAPIConfig(use_handler_docstrings=True, create_examples=True, random_seed=1)
    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()

    receive_op = next(op for op in document.operations.values() if op.action is OperationAction.RECEIVE)
    assert receive_op.description is not None
    assert "Listener docs." in receive_op.description
    assert "Raises:" in receive_op.description
    assert receive_op.messages is not None

    receive_ref = receive_op.messages[0]
    assert isinstance(receive_ref, Reference)
    message_key = receive_ref.ref.split("/")[-1]
    channel = document.channels["/ws"]
    assert channel.messages is not None
    message = channel.messages[message_key]
    assert not isinstance(message, Reference)
    assert message.examples
    assert isinstance(message.examples[0], dict)

    stream_op = next(
        op
        for op in document.operations.values()
        if op.action is OperationAction.SEND and op.channel.ref.endswith("~1stream")
    )
    assert stream_op.description is not None
    assert "Stream docs." in stream_op.description
    assert "Yields:" in stream_op.description
