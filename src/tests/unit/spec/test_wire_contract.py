import pytest

from litestar_asyncapi.spec import Schema


def test_null_literals_are_preserved() -> None:
    assert Schema(examples=[{"value": None, "nested": {"enabled": False}}]).to_schema()["examples"] == [
        {"value": None, "nested": {"enabled": False}}
    ]
    assert Schema(const=None, default=None).to_schema() == {"const": None, "default": None}
    assert Schema().to_schema() == {}


def test_extensions_reject_standard_fields() -> None:
    from litestar_asyncapi.spec import Message

    with pytest.raises(ValueError, match="extension"):
        Message(extensions={"payload": False}).to_schema()


def test_message_examples_formats_and_security() -> None:
    from litestar_asyncapi.spec import Message, MessageExample, MultiFormatSchema, OperationTrait, Reference, Server

    assert MessageExample().to_schema() == {}
    assert MessageExample(payload=None).to_schema() == {"payload": None}
    assert Message(payload=False).to_schema() == {"payload": False}
    assert Message(payload=MultiFormatSchema("application/example", {"value": None})).to_schema() == {
        "payload": {"schemaFormat": "application/example", "schema": {"value": None}}
    }
    security = [Reference("#/components/securitySchemes/token")]
    assert OperationTrait(security=security).to_schema()["security"] == [{"$ref": security[0].ref}]
    assert Server(host="localhost", protocol="ws", security=security).to_schema()["security"] == [
        {"$ref": security[0].ref}
    ]


def test_explicit_legacy_version_and_extensions() -> None:
    from litestar_asyncapi.spec import AsyncAPI, Info, Message, ServerVariable

    assert AsyncAPI(info=Info("Example", "1"), asyncapi="3.0.0").to_schema()["asyncapi"] == "3.0.0"
    assert ServerVariable().to_schema() == {}
    assert Message(extensions={"x-example": {"value": None}}).to_schema() == {"x-example": {"value": None}}


def test_deepcopy_omission_and_ordinary_enums() -> None:
    from copy import deepcopy
    from enum import Enum

    from litestar_asyncapi.spec import MessageExample
    from litestar_asyncapi.spec.base import UNSET

    class Choice(Enum):
        VALUE = "value"

    assert deepcopy(UNSET) is UNSET
    assert deepcopy(Schema()).to_schema() == {}
    assert deepcopy(MessageExample(payload=None)).to_schema() == {"payload": None}
    assert Schema(default=Choice.VALUE).to_schema() == {"default": "value"}
