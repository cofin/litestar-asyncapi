import pytest

from litestar_asyncapi.spec.bindings import AMQPChannelBinding, KafkaChannelBinding

pytestmark = pytest.mark.anyio


def test_optional_bindings_serialize() -> None:
    kafka = KafkaChannelBinding(binding_version="0.5.0", topic="events", partitions=3)
    data = kafka.to_schema()
    assert data["bindingVersion"] == "0.5.0"
    assert data["topic"] == "events"
    assert data["partitions"] == 3

    amqp = AMQPChannelBinding(binding_version="0.3.0", is_="routingKey", queue={"name": "q"})
    data2 = amqp.to_schema()
    assert data2["bindingVersion"] == "0.3.0"
    assert data2["is"] == "routingKey"
    assert data2["queue"]["name"] == "q"
