from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import AsyncAPI, OperationAction, Reference, Schema, SchemaType

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import WebSocket

pytestmark = pytest.mark.anyio


def test_generator_builds_document_with_channels_and_operations() -> None:
    from litestar import Litestar, websocket_listener
    from litestar.handlers.websocket_handlers.stream import websocket_stream

    @dataclass
    class Payload:
        value: int

    @websocket_listener("/listen", signature_namespace={"Payload": Payload})
    async def listener(socket: "WebSocket", data: Payload) -> Payload:
        raise RuntimeError

    @websocket_stream("/stream", signature_namespace={"Payload": Payload})
    async def stream() -> "AsyncGenerator[Payload, None]":
        if TYPE_CHECKING:  # pragma: no cover
            yield Payload(value=1)

    app = Litestar(route_handlers=[listener, stream])

    from litestar_asyncapi import AsyncAPIConfig

    config = AsyncAPIConfig(title="Test", version="1.0.0", description="desc")
    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()

    assert isinstance(document, AsyncAPI)
    assert document.asyncapi == "3.1.0"
    assert document.info.title == "Test"
    assert document.default_content_type is None
    assert "/listen" in document.channels
    assert "/stream" in document.channels
    assert {op.action for op in document.operations.values()} == {OperationAction.RECEIVE, OperationAction.SEND}

    receive = next(op for op in document.operations.values() if op.action is OperationAction.RECEIVE)
    assert receive.messages is not None
    assert isinstance(receive.messages[0], Reference)
    channel = document.channels["/listen"]
    assert channel.messages is not None
    message_key = receive.messages[0].ref.split("/")[-1]
    assert message_key in channel.messages


def test_generator_ensures_unique_operation_ids_for_channels_plugin() -> None:
    from litestar import Litestar
    from litestar.channels.backends.memory import MemoryChannelsBackend
    from litestar.channels.plugin import ChannelsPlugin

    from litestar_asyncapi import AsyncAPIConfig

    plugin = ChannelsPlugin(MemoryChannelsBackend(), channels=["news", "alerts"], create_ws_route_handlers=False)
    app = Litestar(route_handlers=[], plugins=[plugin])
    config = AsyncAPIConfig(include_websocket_routes=False, include_channels_plugin=True)

    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()
    operation_ids = list(document.operations)

    assert all(operation_ids)
    assert len(operation_ids) == len(set(operation_ids))


def test_conflicting_discovered_channels_do_not_overwrite() -> None:
    from litestar import Litestar, websocket_listener
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig

    @websocket_listener("/same")
    async def first(data: str) -> None:
        return None

    @websocket_listener("/same")
    async def second(data: int) -> None:
        return None

    with pytest.raises(
        ImproperlyConfiguredException,
        match=r"Conflicting channel '/same': route /same handler first and route /same handler second",
    ):
        AsyncAPIGenerator(Litestar([second, first]), AsyncAPIConfig()).build_schema()


@pytest.mark.parametrize(
    ("payload", "content_type"),
    [
        (Reference(ref="#/components/schemas/User"), "application/json"),
        (Schema(type=SchemaType.OBJECT, properties={"id": Schema(type=SchemaType.INTEGER)}), "application/json"),
        (Schema(type=SchemaType.ARRAY), "application/json"),
        (Schema(), None),
    ],
)
def test_message_content_type_is_inferred_only_for_structured_payloads(
    payload: Schema | Reference, content_type: str | None
) -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
    from litestar_asyncapi.spec import Components

    config = AsyncAPIConfig(
        components=Components(schemas={"User": Schema(type=SchemaType.OBJECT)}),
        channels=[
            ChannelDefinition(
                "events",
                "/events",
                [OperationDefinition(action="send", messages=[MessageDefinition(name="Event", payload=payload)])],
            )
        ],
    )
    message = AsyncAPIGenerator(Litestar([]), config).build_schema()["channels"]["events"]["messages"]["Event"]
    assert message.get("contentType") == content_type


def test_operation_id_case_insensitive_collision() -> None:
    from litestar import Litestar, websocket

    from litestar_asyncapi import AsyncAPIConfig

    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: "WebSocket") -> None:
        return None

    @websocket("/op2", operation_id="MYOP")
    async def handler2(socket: "WebSocket") -> None:
        return None

    config = AsyncAPIConfig(include_raw_websocket_routes=True)
    with pytest.warns(UserWarning, match="cannot infer the raw WebSocket"):
        operations = AsyncAPIGenerator(Litestar([handler1, handler2]), config).build_asyncapi().operations

    assert len(operations) == 4
    assert len({key.casefold() for key in operations}) == 4


def test_strict_uniqueness_raises_exception() -> None:
    from litestar import Litestar, websocket
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig

    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: "WebSocket") -> None:
        return None

    @websocket("/op2", operation_id="myOp")
    async def handler2(socket: "WebSocket") -> None:
        return None

    config = AsyncAPIConfig(strict_uniqueness=True, include_raw_websocket_routes=True)
    with (
        pytest.warns(UserWarning, match="cannot infer the raw WebSocket"),
        pytest.raises(ImproperlyConfiguredException, match="Duplicate operationId found"),
    ):
        AsyncAPIGenerator(Litestar([handler1, handler2]), config).build_asyncapi()


def test_reversed_explicit_channels_have_stable_sanitized_casefold_keys() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition

    channels = [
        ChannelDefinition(
            key,
            "/shared",
            [OperationDefinition(action="send", operation_id=operation_id, messages=[MessageDefinition(payload=int)])],
        )
        for key, operation_id in [("z", "A/B"), ("a", "a b"), ("c", "A_B")]
    ]
    app = Litestar([])
    first = AsyncAPIGenerator(app, AsyncAPIConfig(channels=channels)).build_schema()
    second = AsyncAPIGenerator(app, AsyncAPIConfig(channels=list(reversed(channels)))).build_schema()
    assert first == second
    assert set(first["channels"]) == {"a", "c", "z"}
    assert list(first["operations"]) == ["a_b", "A_B_2", "A_B_3"]


def test_channel_message_refs_uri_escape_literal_percent() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition

    document = AsyncAPIGenerator(
        Litestar([]),
        AsyncAPIConfig(
            channels=[
                ChannelDefinition(
                    "literal%2F/#",
                    "/socket",
                    [OperationDefinition(action="send", messages=[MessageDefinition(name="m%/~", payload=int)])],
                )
            ]
        ),
    ).build_schema()
    operation = next(iter(document["operations"].values()))
    assert operation["channel"]["$ref"] == "#/channels/literal%252F~1%23"
    assert operation["messages"] == [{"$ref": "#/channels/literal%252F~1%23/messages/m%25~1~0"}]


@pytest.mark.parametrize("send_payload", [str, int])
def test_same_named_message_is_shared_or_rejected_across_operations(send_payload: type) -> None:
    from litestar import Litestar, websocket
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig, asyncapi_message

    @asyncapi_message(action="send", name="Value", payload=send_payload)
    @asyncapi_message(action="receive", name="Value", payload=str)
    @websocket("/values")
    async def values(socket: "WebSocket") -> None:
        return None

    generator = AsyncAPIGenerator(Litestar([values]), AsyncAPIConfig())
    if send_payload is int:
        with pytest.raises(ImproperlyConfiguredException, match="Conflicting message 'Value' on channel '/values'"):
            generator.build_schema()
        return
    document = generator.build_schema()
    assert set(document["channels"]["/values"]["messages"]) == {"Value"}
    assert {operation["messages"][0]["$ref"] for operation in document["operations"].values()} == {
        "#/channels/~1values/messages/Value"
    }
