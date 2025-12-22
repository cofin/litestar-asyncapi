import pytest

from litestar_asyncapi.spec import (
    AsyncAPI,
    Channel,
    Components,
    Info,
    Message,
    Operation,
    OperationAction,
    Reference,
    Schema,
    SchemaType,
)

pytestmark = pytest.mark.anyio


def test_asyncapi_root_serialization() -> None:
    message = Message(name="ChatMessage", payload=Schema(type=SchemaType.OBJECT))
    channel = Channel(address="/chat/{room}", messages={"chat": message})
    operation = Operation(action=OperationAction.RECEIVE, channel=Reference("#/channels/chat"))

    doc = AsyncAPI(
        info=Info(title="My API", version="1.0.0"),
        default_content_type="application/json",
        channels={"chat": channel},
        operations={"receiveChat": operation},
        components=Components(schemas={"ChatPayload": Schema(type=SchemaType.OBJECT)}),
    )

    schema = doc.to_schema()
    assert schema["asyncapi"] == "3.0.0"
    assert schema["info"]["title"] == "My API"
    assert schema["defaultContentType"] == "application/json"
    assert "channels" in schema
    assert schema["channels"]["chat"]["address"] == "/chat/{room}"
    assert schema["channels"]["chat"]["messages"]["chat"]["name"] == "ChatMessage"
    assert schema["operations"]["receiveChat"]["action"] == "receive"
