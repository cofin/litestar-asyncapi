from dataclasses import dataclass
from typing import Any, cast

import pytest
from litestar import Litestar, websocket

from litestar_asyncapi import AsyncAPIConfig, asyncapi_message, asyncapi_operation
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import Message, MessageTrait, OperationAction, OperationTrait, Reference

pytestmark = pytest.mark.anyio


@dataclass
class Payload:
    value: int


def test_traits_are_emitted_and_referenced() -> None:
    config = AsyncAPIConfig(
        title="T",
        version="1",
        operation_traits={"common": OperationTrait(summary="s")},
        message_traits={"commonMsg": MessageTrait(summary="m")},
    )

    @asyncapi_operation(action=OperationAction.RECEIVE, traits=["common"])
    @asyncapi_message(action="receive", payload=Payload, traits=["commonMsg"])
    @websocket("/ws")
    async def handler(socket: Any) -> None:
        return None

    app = Litestar(route_handlers=[handler])
    document = AsyncAPIGenerator(app=app, config=config).build_asyncapi()

    assert "common" in document.components.operation_traits
    assert "commonMsg" in document.components.message_traits

    receive = next(op for op in document.operations.values() if op.action is OperationAction.RECEIVE)
    assert receive.traits is not None
    assert isinstance(receive.traits[0], Reference)
    assert receive.traits[0].ref == "#/components/operationTraits/common"

    assert receive.messages is not None
    msg_ref = receive.messages[0]
    assert isinstance(msg_ref, Reference)
    assert msg_ref.ref.startswith("#/channels/")

    channel = document.channels["/ws"]
    assert channel.messages is not None
    message_key = msg_ref.ref.split("/")[-1]
    msg = cast("Message", channel.messages[message_key])
    assert msg.traits is not None
    assert isinstance(msg.traits[0], Reference)
    assert msg.traits[0].ref == "#/components/messageTraits/commonMsg"
