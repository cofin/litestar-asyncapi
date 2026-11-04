from collections.abc import AsyncGenerator

import pytest
from litestar import Litestar, get
from litestar.exceptions import ImproperlyConfiguredException
from litestar.response import ServerSentEvent, Stream

from litestar_asyncapi import AsyncAPIConfig, asyncapi_message, asyncapi_operation
from litestar_asyncapi.asyncapi.extractors import extract_sse_channels
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


async def _lines() -> AsyncGenerator[str, None]:
    yield "line"


def test_plain_stream_routes_are_not_server_sent_events() -> None:
    @get("/download")
    async def download() -> Stream:
        return Stream(_lines())

    app = Litestar([download])
    assert extract_sse_channels(app, schema_generator=AsyncAPISchemaGenerator(app), config=AsyncAPIConfig()) == []


def test_server_sent_event_operation_metadata_comes_from_decorators() -> None:
    @asyncapi_operation(action="send", operation_id="streamPrices", summary="Price stream")
    @get("/prices", summary="HTTP summary")
    async def prices() -> ServerSentEvent:
        return ServerSentEvent(_lines())

    document = AsyncAPIGenerator(Litestar([prices]), AsyncAPIConfig()).build_schema()
    assert document["operations"]["streamPrices"]["summary"] == "Price stream"


def test_server_sent_event_route_rejects_receive_declarations() -> None:
    @asyncapi_message(action="receive", payload=str)
    @get("/upload")
    async def upload() -> ServerSentEvent:
        return ServerSentEvent(_lines())

    with pytest.raises(ImproperlyConfiguredException, match=r"Server-Sent Event route /upload .* only send"):
        AsyncAPIGenerator(Litestar([upload]), AsyncAPIConfig()).build_schema()
