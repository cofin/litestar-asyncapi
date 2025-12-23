from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import OperationAction, Reference

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

pytestmark = pytest.mark.anyio


def test_stream_infers_send_operation_from_item_type() -> None:
    from litestar import Litestar
    from litestar.handlers.websocket_handlers.stream import websocket_stream

    @dataclass
    class StreamItem:
        value: int

    @websocket_stream("/stream", signature_namespace={"StreamItem": StreamItem})
    async def handler() -> "AsyncGenerator[StreamItem, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield StreamItem(value=1)

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    assert [op.action for op in channel.operations] == [OperationAction.SEND]
    operation = channel.operations[0]
    assert operation.message is not None
    assert isinstance(operation.message.payload, Reference)
