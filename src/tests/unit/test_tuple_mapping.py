from typing import Tuple
from litestar.typing import FieldDefinition
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import SchemaType


def test_fixed_length_tuple_mapping() -> None:
    generator = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(Tuple[int, str])
    
    schema = generator.generate_schema(field)
    
    assert schema.type == SchemaType.ARRAY
    assert schema.prefix_items is not None
    assert len(schema.prefix_items) == 2
    assert schema.prefix_items[0].type == SchemaType.INTEGER
    assert schema.prefix_items[1].type == SchemaType.STRING
    assert schema.min_items == 2
    assert schema.max_items == 2


def test_variadic_tuple_mapping() -> None:
    generator = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(Tuple[int, ...])
    
    schema = generator.generate_schema(field)
    
    assert schema.type == SchemaType.ARRAY
    assert schema.items is not None
    assert schema.items.type == SchemaType.INTEGER
    assert schema.prefix_items is None
