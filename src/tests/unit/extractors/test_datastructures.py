import pytest

from litestar_asyncapi._asyncapi.datastructures import DiscoveredChannel, DiscoveredMessage, DiscoverySource
from litestar_asyncapi.spec import Message, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_discovered_message_to_spec_message() -> None:
    payload = Schema(type=SchemaType.OBJECT)
    discovered = DiscoveredMessage(name="UserCreated", payload=payload, content_type="application/json")

    message = discovered.to_spec_message()
    assert isinstance(message, Message)
    assert message.name == "UserCreated"
    assert message.content_type == "application/json"
    assert isinstance(message.payload, Schema)
    assert message.payload.type == SchemaType.OBJECT


def test_discovered_channel_defaults() -> None:
    channel = DiscoveredChannel(address="/ws/{room}", source=DiscoverySource.WEBSOCKET)
    assert channel.parameters is None
    assert channel.operations == ()
