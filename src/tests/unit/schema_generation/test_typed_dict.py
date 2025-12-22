import pytest
from litestar.typing import FieldDefinition
from typing_extensions import NotRequired, TypedDict

from litestar_asyncapi._asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


class Payload(TypedDict):
    id: int
    note: NotRequired[str]


def test_typed_dict_schema_is_componentized() -> None:
    gen = AsyncAPISchemaGenerator()
    ref = gen.generate_schema(FieldDefinition.from_annotation(Payload))
    assert isinstance(ref, Reference)

    components = gen.schema_registry.generate_components_schemas()
    assert "Payload" in components
    schema = components["Payload"]
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.OBJECT
    assert schema.required == ["id"]
