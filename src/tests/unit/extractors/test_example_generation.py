from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, websocket_listener
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def test_examples_generated_for_listener_messages() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_listener("/ws", signature_namespace={"Payload": Payload})
    async def handler(data: Payload) -> Payload:
        raise RuntimeError

    document = AsyncAPIGenerator(Litestar([handler]), AsyncAPIConfig(create_examples=True)).build_schema()
    messages = document["channels"]["/ws"]["messages"]
    assert len(messages) == 2
    for message in messages.values():
        assert isinstance(message["examples"][0]["payload"]["value"], int)


def test_examples_generated_for_stream_messages() -> None:
    @dataclass
    class Payload:
        value: int

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        yield Payload(value=1)

    document = AsyncAPIGenerator(Litestar([stream]), AsyncAPIConfig(create_examples=True)).build_schema()
    message = next(iter(document["channels"]["/stream"]["messages"].values()))
    assert isinstance(message["examples"][0]["payload"]["value"], int)
