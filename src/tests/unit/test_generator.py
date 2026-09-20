from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import AsyncAPI, OperationAction, Reference

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


def test_conflicting_discovered_channels_do_not_overwrite(monkeypatch) -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.datastructures import DiscoveredChannel, DiscoverySource
    from litestar_asyncapi.spec import Parameter

    channels = [
        DiscoveredChannel(
            route_identity=None,
            key="same",
            address="/same",
            source=DiscoverySource.WEBSOCKET,
            provenance="first handler",
            parameters={"id": Parameter(description="first")},
        ),
        DiscoveredChannel(
            route_identity=None,
            key="same",
            address="/same",
            source=DiscoverySource.WEBSOCKET,
            provenance="second handler",
            parameters={"id": Parameter(description="second")},
        ),
    ]
    monkeypatch.setattr(
        "litestar_asyncapi.asyncapi.generator.extract_websocket_channels", lambda *args, **kwargs: channels
    )
    with pytest.raises(ImproperlyConfiguredException, match=r"first handler.*second handler"):
        AsyncAPIGenerator(Litestar([]), AsyncAPIConfig()).build_schema()


def test_same_route_merge_is_stable_and_selects_only_its_messages(monkeypatch) -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, MessageDefinition
    from litestar_asyncapi.asyncapi.datastructures import DiscoveredChannel, DiscoveredOperation, DiscoverySource

    route = object()
    channels = [
        DiscoveredChannel(
            key="path/~key",
            address="/socket",
            route_identity=route,
            source=DiscoverySource.WEBSOCKET,
            provenance=source,
            operations=[
                DiscoveredOperation(
                    action="send",
                    operation_id="same / id",
                    provenance=source,
                    messages=[MessageDefinition(name=name, payload=payload)],
                )
            ],
        )
        for source, name, payload in [("second", "b/~", str), ("first", "a", int)]
    ]
    monkeypatch.setattr(
        "litestar_asyncapi.asyncapi.generator.extract_websocket_channels", lambda *args, **kwargs: channels
    )
    first = AsyncAPIGenerator(Litestar([]), AsyncAPIConfig()).build_schema()
    channels.reverse()
    second = AsyncAPIGenerator(Litestar([]), AsyncAPIConfig()).build_schema()
    assert first == second
    assert list(first["operations"]) == ["same_id"]
    operation = first["operations"]["same_id"]
    assert operation["channel"]["$ref"] == "#/channels/path~1~0key"
    assert {ref["$ref"] for ref in operation["messages"]} == {
        "#/channels/path~1~0key/messages/a",
        "#/channels/path~1~0key/messages/b~1~0",
    }


def test_shared_named_message_constraints_cannot_be_deduplicated(monkeypatch) -> None:
    from litestar import Litestar
    from litestar.exceptions import ImproperlyConfiguredException
    from litestar.params import Parameter
    from litestar.typing import FieldDefinition

    from litestar_asyncapi import AsyncAPIConfig, MessageDefinition
    from litestar_asyncapi.asyncapi.datastructures import DiscoveredChannel, DiscoveredOperation, DiscoverySource

    route = object()
    channels = [
        DiscoveredChannel(
            key="same",
            address="/same",
            route_identity=route,
            source=DiscoverySource.WEBSOCKET,
            provenance=str(bound),
            operations=[
                DiscoveredOperation(
                    action="send",
                    provenance=str(bound),
                    messages=[
                        MessageDefinition(
                            name="value",
                            payload=FieldDefinition.from_annotation(str, kwarg_definition=Parameter(min_length=bound)),
                        )
                    ],
                )
            ],
        )
        for bound in (1, 5)
    ]
    monkeypatch.setattr(
        "litestar_asyncapi.asyncapi.generator.extract_websocket_channels", lambda *args, **kwargs: channels
    )
    with pytest.raises(ImproperlyConfiguredException, match="Conflicting message"):
        AsyncAPIGenerator(Litestar([]), AsyncAPIConfig()).build_schema()
