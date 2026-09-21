import pytest
from litestar import Litestar, websocket
from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi import AsyncAPIConfig
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator


def test_operation_id_case_insensitive_collision() -> None:
    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: any) -> None:
        pass

    @websocket("/op2", operation_id="MYOP")
    async def handler2(socket: any) -> None:
        pass

    app = Litestar(route_handlers=[handler1, handler2])
    config = AsyncAPIConfig(include_raw_websocket_routes=True)
    generator = AsyncAPIGenerator(app, config)

    with pytest.warns(UserWarning, match="cannot infer the raw WebSocket"):
        schema = generator.build_asyncapi()

    op_ids = list(schema.operations)

    # Should have 4 unique IDs, not a collision on 'myop_receive'
    assert len(op_ids) == 4
    # All should be unique case-insensitively
    assert len({oid.casefold() for oid in op_ids}) == 4


def test_strict_uniqueness_raises_exception() -> None:
    @websocket("/op1", operation_id="myOp")
    async def handler1(socket: any) -> None:
        pass

    @websocket("/op2", operation_id="myOp")
    async def handler2(socket: any) -> None:
        pass

    app = Litestar(route_handlers=[handler1, handler2])
    # Assuming we will add strict_uniqueness to AsyncAPIConfig
    config = AsyncAPIConfig(strict_uniqueness=True, include_raw_websocket_routes=True)
    generator = AsyncAPIGenerator(app, config)

    with (
        pytest.warns(UserWarning, match="cannot infer the raw WebSocket"),
        pytest.raises(ImproperlyConfiguredException, match="Duplicate operationId found"),
    ):
        generator.build_asyncapi()


def test_reversed_explicit_channels_have_stable_sanitized_casefold_keys() -> None:
    from litestar_asyncapi import ChannelDefinition, MessageDefinition, OperationDefinition

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
    from litestar_asyncapi import ChannelDefinition, MessageDefinition, OperationDefinition

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
