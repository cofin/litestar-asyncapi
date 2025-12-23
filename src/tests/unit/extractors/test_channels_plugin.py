import pytest

from litestar_asyncapi.asyncapi.extractors import extract_channels_plugin_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_channels_plugin_extracts_declared_channels() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=False)
    app = Litestar(route_handlers=[], plugins=[plugin])
    gen = AsyncAPISchemaGenerator()

    channels = extract_channels_plugin_channels(app, schema_generator=gen)
    assert {c.address for c in channels} == {"/news", "/alerts"}
    assert all(c.operations for c in channels)


def test_channels_plugin_extractor_returns_empty_without_plugin() -> None:
    from litestar import Litestar

    app = Litestar(route_handlers=[], plugins=[])
    gen = AsyncAPISchemaGenerator()

    assert extract_channels_plugin_channels(app, schema_generator=gen) == []


def test_channels_plugin_is_noop_when_ws_route_handlers_are_created() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news"], create_ws_route_handlers=True)
    app = Litestar(route_handlers=[], plugins=[plugin])
    gen = AsyncAPISchemaGenerator()

    assert extract_channels_plugin_channels(app, schema_generator=gen) == []


def test_channels_plugin_arbitrary_channels_yields_wildcard_channel() -> None:
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
    assert [c.address for c in channels] == ["/ws/{channel_name}"]
    assert channels[0].parameters is not None
    assert "channel_name" in channels[0].parameters
    assert isinstance(channels[0].parameters["channel_name"].schema, Schema)
    assert channels[0].parameters["channel_name"].schema.type == SchemaType.STRING
