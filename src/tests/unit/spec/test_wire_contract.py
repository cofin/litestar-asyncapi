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


def test_kafka_binding_keys_match_official_schema() -> None:
    from litestar_asyncapi.spec.bindings import KafkaMessageBinding, KafkaServerBinding

    assert KafkaServerBinding(
        schema_registry_url="https://registry", schema_registry_vendor="confluent"
    ).to_schema() == {"schemaRegistryUrl": "https://registry", "schemaRegistryVendor": "confluent"}
    assert KafkaMessageBinding(
        schema_id_location="payload", schema_id_payload_encoding="confluent", schema_lookup_strategy="TopicIdStrategy"
    ).to_schema() == {
        "schemaIdLocation": "payload",
        "schemaIdPayloadEncoding": "confluent",
        "schemaLookupStrategy": "TopicIdStrategy",
    }


def test_keys_without_alias_are_camel_cased() -> None:
    from dataclasses import dataclass, field

    from litestar_asyncapi.spec.base import BaseSchemaObject

    @dataclass(slots=True)
    class Session(BaseSchemaObject):
        logged_in: bool
        schema_name: str
        location: str = field(metadata={"alias": "in"})

    assert Session(logged_in=True, schema_name="orders", location="header").to_schema() == {
        "loggedIn": True,
        "schemaName": "orders",
        "in": "header",
    }


def test_non_string_alias_is_rejected() -> None:
    from dataclasses import dataclass, field

    from litestar_asyncapi.spec.base import BaseSchemaObject

    @dataclass(slots=True)
    class Invalid(BaseSchemaObject):
        value: int = field(default=1, metadata={"alias": 1})

    with pytest.raises(TypeError, match=r'metadata\["alias"\] must be a str'):
        Invalid().to_schema()


def test_prefix_items_export_as_draft07_tuple_items() -> None:
    from litestar_asyncapi.spec import SchemaType

    pair = [Schema(type=SchemaType.STRING), Schema(type=SchemaType.INTEGER)]
    wire_pair = [{"type": "string"}, {"type": "integer"}]

    assert Schema(prefix_items=pair).to_schema() == {"items": wire_pair}
    assert Schema(
        type=SchemaType.ARRAY, prefix_items=pair, items=Schema(type=SchemaType.BOOLEAN), min_items=2
    ).to_schema() == {"type": "array", "items": wire_pair, "additionalItems": {"type": "boolean"}, "minItems": 2}
    assert Schema(prefix_items=pair, additional_items=False).to_schema() == {
        "items": wire_pair,
        "additionalItems": False,
    }
    assert Schema(prefix_items=[], items=Schema(type=SchemaType.STRING)).to_schema() == {"items": {"type": "string"}}
    assert Schema(properties={"pair": Schema(prefix_items=pair)}).to_schema() == {
        "properties": {"pair": {"items": wire_pair}}
    }


def test_prefix_items_reject_ambiguous_tuple_keywords() -> None:
    from litestar_asyncapi.spec import SchemaType

    pair = [Schema(type=SchemaType.STRING)]
    with pytest.raises(ValueError, match="items and additionalItems cannot both accompany prefixItems"):
        Schema(prefix_items=pair, items=Schema(type=SchemaType.STRING), additional_items=False).to_schema()
    with pytest.raises(ValueError, match="items must be a single schema when prefixItems is present"):
        Schema(prefix_items=pair, items=[Schema(type=SchemaType.STRING)]).to_schema()
