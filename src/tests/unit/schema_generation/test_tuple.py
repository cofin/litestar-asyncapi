import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_fixed_length_tuple_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(tuple[int, str]))

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert schema.min_items == 2
    assert schema.max_items == 2
    assert isinstance(schema.items, Schema)
    assert schema.items.one_of is not None
    item_types = [item.type for item in schema.items.one_of if isinstance(item, Schema)]
    assert SchemaType.INTEGER in item_types
    assert SchemaType.STRING in item_types


def test_variadic_tuple_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(tuple[int, ...]))

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert isinstance(schema.items, Schema)
    assert schema.items.type == SchemaType.INTEGER
