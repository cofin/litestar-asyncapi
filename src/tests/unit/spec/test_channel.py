import pytest

from litestar_asyncapi.spec import Channel, Message, Parameter, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_channel_serialization_with_parameters_and_messages() -> None:
    channel = Channel(
        address="/chat/{room}",
        parameters={"room": Parameter(schema=Schema(type=SchemaType.STRING))},
        messages={"chat": Message(name="Chat", payload=Schema(type=SchemaType.OBJECT))},
    )

    schema = channel.to_schema()
    assert schema["address"] == "/chat/{room}"
    assert schema["parameters"]["room"]["schema"]["type"] == "string"
    assert schema["messages"]["chat"]["payload"]["type"] == "object"
