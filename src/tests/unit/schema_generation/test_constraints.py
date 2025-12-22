import pytest
from litestar.params import Parameter
from litestar.typing import FieldDefinition

from litestar_asyncapi._asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_string_constraints_are_applied() -> None:
    gen = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(
        str, kwarg_definition=Parameter(min_length=2, max_length=5, pattern="^[a-z]+$")
    )
    schema = gen.generate_schema(field)

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.STRING
    assert schema.min_length == 2
    assert schema.max_length == 5
    assert schema.pattern == "^[a-z]+$"


def test_numeric_constraints_are_applied() -> None:
    gen = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(int, kwarg_definition=Parameter(gt=1, le=10, multiple_of=2))
    schema = gen.generate_schema(field)

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.INTEGER
    assert schema.exclusive_minimum == 1
    assert schema.maximum == 10
    assert schema.multiple_of == 2


def test_array_constraints_are_applied() -> None:
    gen = AsyncAPISchemaGenerator()
    field = FieldDefinition.from_annotation(list[int], kwarg_definition=Parameter(min_items=1, max_items=3))
    schema = gen.generate_schema(field)

    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert schema.min_items == 1
    assert schema.max_items == 3
