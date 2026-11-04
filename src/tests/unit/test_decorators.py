from typing import Any

import pytest
from litestar import websocket_listener

from litestar_asyncapi.decorators import ASYNCAPI_OPT_KEY, AsyncAPIMetadata, asyncapi_message, asyncapi_operation
from litestar_asyncapi.spec import OperationAction

pytestmark = pytest.mark.anyio


def test_decorators_attach_metadata_to_handler_opt() -> None:
    def fn(socket: Any, data: Any) -> Any:
        return None

    handler = websocket_listener("/ws")(fn)
    asyncapi_operation(action="receive", operation_id="recv", summary="in")(handler)
    asyncapi_message(action=OperationAction.RECEIVE, payload=int, name="Inbound")(handler)

    assert ASYNCAPI_OPT_KEY in handler.opt
    metadata = handler.opt[ASYNCAPI_OPT_KEY]
    assert isinstance(metadata, AsyncAPIMetadata)
    operation = metadata.operations[OperationAction.RECEIVE]
    assert operation.operation_id == "recv"
    assert operation.summary == "in"
    assert operation.messages[0] is not None
    assert operation.messages[0].name == "Inbound"
    assert operation.messages[0].payload is int


def test_named_messages_are_preserved_as_choices() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @asyncapi_message(action="receive", name="Number", payload=int)
    @asyncapi_message(action="receive", name="Text", payload=str)
    @websocket_listener("/choices")
    async def handler(data: str) -> None:
        return None

    schema = AsyncAPIGenerator(Litestar([handler]), AsyncAPIConfig()).build_schema()
    assert {message["name"] for message in schema["channels"]["/choices"]["messages"].values()} == {"Number", "Text"}


def test_repeated_message_name_and_unnamed_repeat_fail() -> None:
    from litestar.exceptions import ImproperlyConfiguredException

    async def fn(data: str) -> None:
        return None

    handler = websocket_listener("/names")(fn)
    asyncapi_message(action="receive", name="Value", payload=str)(handler)
    with pytest.raises(ValueError, match="Conflicting message declarations for 'Value'"):
        asyncapi_message(action="receive", name="Value", payload=int)(handler)
    messages = handler.opt[ASYNCAPI_OPT_KEY].operations[OperationAction.RECEIVE].messages
    assert [message.payload for message in messages] == [str]
    with pytest.raises(ImproperlyConfiguredException, match=r"Ambiguous unnamed.*/names.*handler fn:"):
        asyncapi_message(action="receive", payload=bool)(handler)


@pytest.mark.parametrize("message_first", [True, False])
def test_operation_and_message_decorators_merge_in_either_order(message_first: bool) -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig, MessageDefinition
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    async def fn(data: str) -> None:
        return None

    operation = asyncapi_operation(
        action="receive", summary="in", messages=[MessageDefinition(name="Text", payload=str)]
    )
    message = asyncapi_message(action="receive", name="Number", payload=int)
    first, second = (message, operation) if message_first else (operation, message)
    handler = second(first(websocket_listener("/merge")(fn)))

    schema = AsyncAPIGenerator(Litestar([handler]), AsyncAPIConfig()).build_schema()
    assert {item["name"] for item in schema["channels"]["/merge"]["messages"].values()} == {"Number", "Text"}
    assert schema["operations"]["fn_receive"]["summary"] == "in"
    assert len(schema["operations"]["fn_receive"]["messages"]) == 2


@pytest.mark.parametrize("message_first", [True, False])
def test_conflicting_message_name_across_decorators_fails_in_either_order(message_first: bool) -> None:
    from litestar_asyncapi import MessageDefinition

    async def fn(data: str) -> None:
        return None

    operation = asyncapi_operation(action="receive", messages=[MessageDefinition(name="Value", payload=str)])
    message = asyncapi_message(action="receive", name="Value", payload=int)
    first, second = (message, operation) if message_first else (operation, message)
    handler = first(websocket_listener("/conflict")(fn))
    with pytest.raises(ValueError, match="Conflicting message declarations for 'Value' in operation 'receive'"):
        second(handler)


def test_empty_operation_messages_override_inference() -> None:
    from litestar import Litestar

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator

    @asyncapi_operation(action="receive", messages=[])
    @websocket_listener("/no-messages")
    async def handler(data: int) -> None:
        return None

    document = AsyncAPIGenerator(Litestar([handler]), AsyncAPIConfig()).build_schema()
    assert next(iter(document["operations"].values()))["messages"] == []
    assert not document["channels"]["/no-messages"].get("messages")
