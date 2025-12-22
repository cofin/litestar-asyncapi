import pytest

from litestar_asyncapi.spec import Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_schema_serialization_aliases_and_composition() -> None:
    schema = Schema(
        type=SchemaType.OBJECT,
        not_=Schema(type=SchemaType.NULL),
        one_of=[Schema(type=SchemaType.STRING), Schema(type=SchemaType.INTEGER)],
    )

    data = schema.to_schema()
    assert data["type"] == "object"
    assert "not" in data
    assert data["not"]["type"] == "null"
    assert data["oneOf"][0]["type"] == "string"
