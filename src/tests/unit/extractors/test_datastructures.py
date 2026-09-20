import pytest

from litestar_asyncapi.asyncapi.datastructures import DiscoveredChannel, DiscoverySource, MessageDefinition
from litestar_asyncapi.spec import Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_message_definition_retains_payload_contract() -> None:
    payload = Schema(type=SchemaType.OBJECT)
    discovered = MessageDefinition(name="UserCreated", payload=payload, content_type="application/json")

    message = discovered
    assert message.name == "UserCreated"
    assert message.content_type == "application/json"
    assert isinstance(message.payload, Schema)
    assert message.payload.type == SchemaType.OBJECT


def test_discovered_channel_defaults() -> None:
    channel = DiscoveredChannel(key="room", address="/ws/{room}", source=DiscoverySource.WEBSOCKET, provenance="test")
    assert channel.parameters is None
    assert channel.operations == ()


def test_explicit_contracts_preserve_metadata_and_replace_only_matching_key() -> None:
    from litestar import Litestar, websocket_listener

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator, _discover_channels
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
    from litestar_asyncapi.spec import CorrelationId, OperationAction, Reference, Reply, SecurityScheme, Tag

    @websocket_listener("/same")
    async def handler(data: str) -> None:
        return None

    operation = OperationDefinition(
        action="send",
        operation_id="published",
        tags=[Tag(name="events")],
        security=[SecurityScheme(type="userPassword")],
        bindings={"ws": {}},
        reply=Reply(channel=Reference(ref="#/channels/other")),
        messages=[
            MessageDefinition(
                name="first",
                payload=int,
                headers=dict[str, str],
                correlation_id=CorrelationId(location="$message.header#/id"),
            )
        ],
    )
    config = AsyncAPIConfig(
        channels=[
            ChannelDefinition(
                key="/same",
                address="different",
                operations=[operation],
                servers=[Reference(ref="#/servers/main")],
                bindings={"ws": {}},
            ),
            ChannelDefinition(key="other", address="/same"),
        ]
    )
    app = Litestar([handler])
    channels = _discover_channels(app, config, AsyncAPISchemaGenerator(app))
    assert [(channel.key, channel.address) for channel in channels] == [("/same", "different"), ("other", "/same")]
    assert channels[0].operations[0].messages[0].payload is int
    assert channels[0].source is DiscoverySource.CONFIG
    assert "channels[0]" in channels[0].provenance
    assert "operations[0]" in channels[0].operations[0].provenance
    document = AsyncAPIGenerator(app, config).build_schema()
    assert document["operations"]["published"]["action"] == OperationAction.SEND
    assert document["operations"]["published"]["security"] == [{"type": "userPassword"}]
    assert document["operations"]["published"]["reply"]["channel"] == {"$ref": "#/channels/other"}
    assert document["operations"]["published"]["tags"] == [{"name": "events"}]
    assert document["channels"]["/same"]["messages"]["first"]["correlationId"]["location"] == "$message.header#/id"
    assert operation.messages[0].payload is int


def test_explicit_channel_conflicts_identify_both_sources() -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    config = AsyncAPIConfig(channels=[ChannelDefinition("same", "one"), ChannelDefinition("same", "two")])
    with pytest.raises(ImproperlyConfiguredException, match=r"channels\[0\].*channels\[1\]"):
        AsyncAPIGenerator(Litestar([]), config).build_schema()


def test_layered_native_handler_options_supply_typed_definitions() -> None:
    from litestar import Litestar, Router, websocket_listener

    from litestar_asyncapi import MessageDefinition, OperationDefinition, asyncapi_operation
    from litestar_asyncapi.asyncapi.extractors import extract_websocket_channels
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
    from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata
    from litestar_asyncapi.spec import OperationAction

    @websocket_listener("/inherited")
    async def inherited(data: str) -> None:
        return None

    @asyncapi_operation(action="receive", summary="handler wins")
    @websocket_listener("/local")
    async def local(data: str) -> None:
        return None

    metadata = AsyncAPIMetadata(
        operations={
            OperationAction.RECEIVE: OperationDefinition(
                action="receive", summary="router", messages=[MessageDefinition(payload=int)]
            )
        }
    )
    app = Litestar([Router("/parent", route_handlers=[inherited, local], opt={ASYNCAPI_OPT_KEY: metadata})])
    channels = extract_websocket_channels(app, schema_generator=AsyncAPISchemaGenerator(app))
    by_path = {channel.address: channel for channel in channels}
    assert by_path["/parent/inherited"].operations[0].summary == "router"
    assert by_path["/parent/inherited"].operations[0].messages[0].payload is int
    assert by_path["/parent/local"].operations[0].summary == "handler wins"
    assert "inherited" in by_path["/parent/inherited"].operations[0].provenance
