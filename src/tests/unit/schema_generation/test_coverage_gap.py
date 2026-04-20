from enum import Enum
from typing import Any, Dict, Optional, Tuple, Union

from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType


def test_empty_tuple_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(Tuple))
    assert schema.type == SchemaType.ARRAY
    assert schema.prefix_items is None
    assert schema.items is None


def test_dict_no_args_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(Dict))
    assert schema.type == SchemaType.OBJECT
    assert isinstance(schema.additional_properties, Schema)
    assert schema.additional_properties.type is None # Any


def test_optional_int_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(Optional[int]))
    assert isinstance(schema, Schema)
    assert schema.one_of is not None
    types = {s.type for s in schema.one_of if isinstance(s, Schema)}
    assert SchemaType.INTEGER in types
    assert SchemaType.NULL in types


class mixedEnum(Enum):
    STR = "a"
    INT = 2 # 1 collides with True in Enums
    FLOAT = 1.1
    BOOL = True
    NONE = None

def test_mixed_enum_schema() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(mixedEnum))
    assert isinstance(schema.type, list)
    assert set(schema.type) == {
        SchemaType.STRING,
        SchemaType.INTEGER,
        SchemaType.NUMBER,
        SchemaType.BOOLEAN,
        SchemaType.NULL,
    }
