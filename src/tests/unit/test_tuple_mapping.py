from typing import cast

from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType


def test_fixed_tuple_mapping() -> None:
    gen = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(tuple[int, str])
    schema = gen.generate_schema(field)

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert schema.prefix_items is not None
    assert len(schema.prefix_items) == 2
    assert cast("Schema", schema.prefix_items[0]).type == SchemaType.INTEGER
    assert cast("Schema", schema.prefix_items[1]).type == SchemaType.STRING
    assert schema.min_items == 2
    assert schema.max_items == 2


def test_variadic_tuple_mapping() -> None:
    gen = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(tuple[int, ...])
    schema = gen.generate_schema(field)

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert schema.items is not None
    assert cast("Schema", schema.items).type == SchemaType.INTEGER
    assert schema.prefix_items is None
