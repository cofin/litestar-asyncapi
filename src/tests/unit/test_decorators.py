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


def test_named_message_replaces_same_name_and_unnamed_repeat_fails() -> None:
    from litestar.exceptions import ImproperlyConfiguredException

    async def fn(data: str) -> None:
        return None

    handler = websocket_listener("/names")(fn)
    asyncapi_message(action="receive", name="Value", payload=str)(handler)
    asyncapi_message(action="receive", name="Value", payload=int)(handler)
    messages = handler.opt[ASYNCAPI_OPT_KEY].operations[OperationAction.RECEIVE].messages
    assert len(messages) == 1
    assert messages[0].payload is int
    with pytest.raises(ImproperlyConfiguredException, match=r"Ambiguous unnamed.*/names"):
        asyncapi_message(action="receive", payload=bool)(handler)


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
