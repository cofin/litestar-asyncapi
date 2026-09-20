import pytest

from litestar_asyncapi.asyncapi.extractors import extract_channels_plugin_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

pytestmark = pytest.mark.anyio


def test_channels_plugin_without_routes_has_no_socket_contracts() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=False)
    app = Litestar(route_handlers=[], plugins=[plugin])
    gen = AsyncAPISchemaGenerator()

    channels = extract_channels_plugin_channels(app, schema_generator=gen)
    assert channels == []


def test_channels_plugin_extractor_returns_empty_without_plugin() -> None:
    from litestar import Litestar

    app = Litestar(route_handlers=[], plugins=[])
    gen = AsyncAPISchemaGenerator()

    assert extract_channels_plugin_channels(app, schema_generator=gen) == []


def test_channels_plugin_extracts_actual_send_only_routes() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news"], create_ws_route_handlers=True)
    app = Litestar(route_handlers=[], plugins=[plugin])
    gen = AsyncAPISchemaGenerator()

    channels = extract_channels_plugin_channels(app, schema_generator=gen)
    assert [channel.address for channel in channels] == ["/news"]
    assert [operation.action.value for operation in channels[0].operations] == ["send"]


def test_internal_arbitrary_channels_do_not_create_socket_contracts() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    plugin = ChannelsPlugin(
        MemoryChannelsBackend(),
        arbitrary_channels_allowed=True,
        create_ws_route_handlers=False,
        ws_handler_base_path="/ws/",
    )
    app = Litestar(route_handlers=[], plugins=[plugin])
    gen = AsyncAPISchemaGenerator()

    channels = extract_channels_plugin_channels(app, schema_generator=gen)
    assert channels == []


@pytest.mark.parametrize("arbitrary", [False, True])
def test_actual_channels_routes_are_deduplicated_by_native_identity(arbitrary: bool) -> None:
    from litestar import Litestar, websocket_listener
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @websocket_listener("/ws/user")
    async def user(data: str) -> str:
        return data

    plugin = ChannelsPlugin(
        MemoryChannelsBackend(),
        channels=["news"],
        arbitrary_channels_allowed=arbitrary,
        create_ws_route_handlers=True,
        ws_handler_base_path="/ws",
    )
    app = Litestar([user], plugins=[plugin])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    generated_path = "/ws/{channel_name}" if arbitrary else "/ws/news"
    assert set(document["channels"]) == {"/ws/user", generated_path}
    actions = [
        operation["action"]
        for operation in document["operations"].values()
        if operation["channel"]["$ref"] == "#/channels/" + generated_path.replace("/", "~1")
    ]
    assert actions == ["send"]
    message = next(iter(document["channels"][generated_path]["messages"].values()))
    assert message["payload"] == {}
    assert message["contentType"] == "text/plain"
    assert message["x-websocket-mode"] == "text"
    hidden = AsyncAPIGenerator(app, AsyncAPIConfig(include_channels_plugin=False)).build_schema()
    assert set(hidden["channels"]) == {"/ws/user"}
