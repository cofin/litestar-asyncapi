from dataclasses import dataclass
from urllib.parse import unquote

import pytest

from litestar_asyncapi.asyncapi.extractors import extract_channels_plugin_channels
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


@pytest.mark.parametrize(("root", "topic"), [("ws", "news"), ("/", "/news"), ("/ws/", "news/")])
def test_generated_route_keeps_original_topic_identity(root: str, topic: str) -> None:
    from litestar import Litestar
    from litestar.channels import ChannelsPlugin
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.utils.path import normalize_path

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    channels = ChannelsPlugin(
        MemoryChannelsBackend(), channels=[topic], ws_handler_base_path=root, create_ws_route_handlers=True
    )
    document = AsyncAPIGenerator(
        Litestar([], plugins=[channels]), AsyncAPIConfig(channel_payloads={topic: int})
    ).build_schema()
    key = normalize_path(root.rstrip("/") + "/" + topic)
    assert set(document["channels"]) == {key}
    message = next(iter(document["channels"][key]["messages"].values()))
    assert message["payload"]["type"] == "integer"
    assert message["contentType"] == "application/json"


def test_configured_topics_without_routes_become_topic_channels() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=False)
    app = Litestar(route_handlers=[], plugins=[plugin])
    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()

    assert set(document["channels"]) == {"news", "alerts"}
    assert document["channels"]["news"] == {
        "address": "news",
        "description": "ChannelsPlugin broker topic",
        "messages": {"news_send": {"payload": {}}},
        "bindings": {},
        "x-litestar-source": "channels",
    }
    assert set(document["operations"]) == {"news_send", "alerts_send"}
    assert document["operations"]["news_send"]["action"] == "send"

    hidden = AsyncAPIGenerator(app, AsyncAPIConfig(include_channels_plugin_topics=False)).build_schema()
    assert hidden["channels"] == {}


@pytest.mark.parametrize("snapshot", [True, False])
def test_runtime_subscriptions_never_reach_the_document(snapshot: bool) -> None:
    import asyncio

    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    channels = ChannelsPlugin(MemoryChannelsBackend(), channels=["news"], arbitrary_channels_allowed=True)
    config = AsyncAPIConfig(docs=DocsConfig(enabled=False), use_cache=False)
    asyncapi = AsyncAPIPlugin(config)
    app = Litestar(route_handlers=[], plugins=[channels, asyncapi] if snapshot else [channels])

    async def subscribe() -> None:
        async with channels:
            await channels.subscribe("runtime")

    asyncio.run(subscribe())
    document = asyncapi.get_asyncapi_schema(app) if snapshot else AsyncAPIGenerator(app, config).build_schema()
    assert set(document["channels"]) == ({"news"} if snapshot else set())


def test_arbitrary_channels_without_snapshot_emit_no_topic_channels() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    arbitrary = ChannelsPlugin(MemoryChannelsBackend(), channels=["news"], arbitrary_channels_allowed=True)
    fixed = ChannelsPlugin(MemoryChannelsBackend(), channels=["alerts"])
    document = AsyncAPIGenerator(Litestar([], plugins=[arbitrary, fixed]), AsyncAPIConfig()).build_schema()
    assert set(document["channels"]) == {"alerts"}


def test_topic_keys_colliding_with_other_channels_raise() -> None:
    from litestar import Litestar, websocket_listener
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @websocket_listener("/live")
    async def live(data: str) -> str:
        return data

    app = Litestar([live], plugins=[ChannelsPlugin(MemoryChannelsBackend(), channels=["/live", "news"])])
    with pytest.raises(
        ImproperlyConfiguredException,
        match=r"Conflicting channel '/live': ChannelsPlugin\[0\] topic '/live' and route /live",
    ):
        AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()

    config = AsyncAPIConfig(channels=[ChannelDefinition("news", "news")], include_websocket_routes=False)
    with pytest.raises(
        ImproperlyConfiguredException, match=r"ChannelsPlugin\[0\] topic 'news'.*AsyncAPIConfig.channels\[0\]"
    ):
        AsyncAPIGenerator(app, config).build_schema()


def test_topic_shared_by_two_channels_plugins_raises() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    app = Litestar(
        [],
        plugins=[
            ChannelsPlugin(MemoryChannelsBackend(), channels=["news"]),
            ChannelsPlugin(MemoryChannelsBackend(), channels=["alerts", "news"]),
        ],
    )
    with pytest.raises(
        ImproperlyConfiguredException, match=r"ChannelsPlugin topic 'news'.*ChannelsPlugin\[0\].*ChannelsPlugin\[1\]"
    ):
        AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()


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
    assert [channel.key for channel in channels] == ["/news"]
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
        if unquote(operation["channel"]["$ref"]) == "#/channels/" + generated_path.replace("/", "~1")
    ]
    assert actions == ["send"]
    message = next(iter(document["channels"][generated_path]["messages"].values()))
    assert message["payload"] == {}
    assert message["contentType"] == "text/plain"
    assert message["x-websocket-mode"] == "text"
    hidden = AsyncAPIGenerator(app, AsyncAPIConfig(include_channels_plugin=False)).build_schema()
    assert set(hidden["channels"]) == {"/ws/user"}


@dataclass
class Headline:
    title: str


def test_channel_payloads_type_generated_routes_and_topic_channels() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    routes = ChannelsPlugin(
        MemoryChannelsBackend(), channels=["news"], create_ws_route_handlers=True, ws_handler_base_path="/ws/"
    )
    topics = ChannelsPlugin(MemoryChannelsBackend(), channels=["orders", "alerts"])
    config = AsyncAPIConfig(channel_payloads={"news": Headline, "orders": Headline})
    document = AsyncAPIGenerator(Litestar([], plugins=[routes, topics]), config).build_schema()
    headline = {"$ref": "#/components/schemas/Headline"}

    assert document["channels"]["/ws/news"]["messages"] == {
        "ws_news_send": {"payload": headline, "contentType": "application/json", "x-websocket-mode": "text"}
    }
    assert document["channels"]["orders"]["messages"] == {
        "orders_send": {"payload": headline, "contentType": "application/json"}
    }
    assert document["channels"]["alerts"]["messages"] == {"alerts_send": {"payload": {}}}
    assert document["components"]["schemas"]["Headline"]["properties"] == {"title": {"type": "string"}}


@pytest.mark.parametrize("flags", [{}, {"include_channels_plugin": False}, {"include_channels_plugin_topics": False}])
def test_channel_payloads_reject_unknown_topics_whatever_the_flags(flags: "dict[str, bool]") -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    config = AsyncAPIConfig(channel_payloads={"missing": Headline}, **flags)
    app = Litestar([], plugins=[ChannelsPlugin(MemoryChannelsBackend(), channels=["news"])])
    with pytest.raises(ImproperlyConfiguredException, match=r"channel_payloads key 'missing' names no configured"):
        AsyncAPIGenerator(app, config).build_schema()
    with pytest.raises(ImproperlyConfiguredException, match=r"channel_payloads key 'missing' names no configured"):
        AsyncAPIGenerator(Litestar([]), config).build_schema()


def test_arbitrary_channels_declare_payload_topics_and_keep_their_route_untyped() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    plugin = ChannelsPlugin(
        MemoryChannelsBackend(),
        arbitrary_channels_allowed=True,
        create_ws_route_handlers=True,
        ws_handler_base_path="/ws/",
    )
    config = AsyncAPIConfig(channel_payloads={"prices": Headline})
    document = AsyncAPIGenerator(Litestar([], plugins=[plugin]), config).build_schema()

    assert set(document["channels"]) == {"/ws/{channel_name}", "prices"}
    assert next(iter(document["channels"]["/ws/{channel_name}"]["messages"].values()))["payload"] == {}
    assert document["channels"]["prices"]["messages"]["prices_send"]["payload"] == {
        "$ref": "#/components/schemas/Headline"
    }
