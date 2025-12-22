import pytest

from litestar_asyncapi.spec import CorrelationId, Message, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_message_serialization_with_payload_and_correlation_id() -> None:
    message = Message(
        name="Event",
        payload=Schema(type=SchemaType.OBJECT),
        correlation_id=CorrelationId(location="$message.header#/correlationId"),
        content_type="application/json",
    )

    schema = message.to_schema()
    assert schema["name"] == "Event"
    assert schema["payload"]["type"] == "object"
    assert schema["correlationId"]["location"] == "$message.header#/correlationId"
    assert schema["contentType"] == "application/json"
