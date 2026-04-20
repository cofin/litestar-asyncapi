import pytest

from litestar_asyncapi.spec import Message, Operation, OperationAction, Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_operation_serialization() -> None:
    operation = Operation(
        action=OperationAction.SEND,
        channel=Reference("#/channels/chat"),
        operation_id="sendChat",
        messages=[Message(name="Chat", payload=Schema(type=SchemaType.OBJECT))],
    )

    schema = operation.to_schema()
    assert schema["action"] == "send"
    assert schema["channel"]["$ref"] == "#/channels/chat"
    assert schema["operationId"] == "sendChat"
    assert schema["messages"][0]["name"] == "Chat"
