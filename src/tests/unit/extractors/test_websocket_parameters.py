from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi._asyncapi.extractors import extract_websocket_channels
from litestar_asyncapi._asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaFormat, SchemaType

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
    assert room_param.location == "path"
    assert isinstance(room_param.schema, Schema)
    assert room_param.schema.type == SchemaType.INTEGER

    when_param = channel.parameters["when"]
    assert when_param.location == "path"
    assert isinstance(when_param.schema, Schema)
    assert when_param.schema.type == SchemaType.STRING
    assert when_param.schema.format == SchemaFormat.DATE
