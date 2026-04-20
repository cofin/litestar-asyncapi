from enum import Enum

from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType


def test_empty_tuple_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(tuple))
    assert schema.type == SchemaType.ARRAY
    assert schema.prefix_items is None
    assert schema.items is None


def test_dict_no_args_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(dict))
    assert schema.type == SchemaType.OBJECT
    assert schema.additional_properties is None


def test_optional_int_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(int | None))
    assert isinstance(schema, Schema)
    assert schema.one_of is not None
    types = {s.type for s in schema.one_of if isinstance(s, Schema)}
    assert SchemaType.INTEGER in types
    assert SchemaType.NULL in types


class MixedEnum(Enum):
    STR = "a"
    INT = 2  # 1 collides with True in Enums
    FLOAT = 1.1
    BOOL = True
    NONE = None


def test_mixed_enum_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(MixedEnum))
    assert isinstance(schema.type, list)
    assert set(schema.type) == {
        SchemaType.STRING,
        SchemaType.INTEGER,
        SchemaType.NUMBER,
        SchemaType.BOOLEAN,
        SchemaType.NULL,
    }
