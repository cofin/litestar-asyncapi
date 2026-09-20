from litestar import Litestar

from litestar_asyncapi import AsyncAPIConfig, ChannelDefinition, MessageDefinition, OperationDefinition
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import MessageExample


def test_explicit_message_examples_normalize_only_at_assembly() -> None:
    example = MessageExample(name="empty", payload=None, headers={"id": "1"})
    definition = MessageDefinition(payload=int | None, examples=[example])
    config = AsyncAPIConfig(
        channels=[ChannelDefinition("events", "events", [OperationDefinition(action="send", messages=[definition])])]
    )
    document = AsyncAPIGenerator(Litestar([]), config).build_schema()
    message = next(iter(document["channels"]["events"]["messages"].values()))
    assert message["examples"] == [{"name": "empty", "payload": None, "headers": {"id": "1"}}]
    assert definition.examples[0] is example
    assert definition.payload == int | None
