from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

if TYPE_CHECKING:
    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_path_parameters_are_converted_to_asyncapi_parameters() -> None:
    from litestar import Litestar, websocket

    @websocket("/ws/{room:int}/{when:date}")
    async def handler(socket: "WebSocket") -> None:
        return None

    app = Litestar(route_handlers=[handler])
    gen = AsyncAPISchemaGenerator()

    channel = extract_websocket_channels(app, schema_generator=gen)[0]
    assert channel.parameters is not None
    assert set(channel.parameters) == {"room", "when"}

    room_param = channel.parameters["room"]
    assert "int" in room_param.description.lower()

    when_param = channel.parameters["when"]
    assert "date" in when_param.description.lower()
