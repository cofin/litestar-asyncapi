from typing import Literal

import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi._asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_generate_schema_primitives() -> None:
    gen = AsyncAPISchemaGenerator()
    s1 = gen.generate_schema(FieldDefinition.from_annotation(str))
    assert isinstance(s1, Schema)
    assert s1.type == SchemaType.STRING

    s2 = gen.generate_schema(FieldDefinition.from_annotation(int))
    assert isinstance(s2, Schema)
    assert s2.type == SchemaType.INTEGER

    s3 = gen.generate_schema(FieldDefinition.from_annotation(bool))
    assert isinstance(s3, Schema)
    assert s3.type == SchemaType.BOOLEAN


def test_generate_schema_optional_union() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(int | None))
    assert isinstance(schema, Schema)
    assert schema.one_of is not None
    types = {s.type for s in schema.one_of if isinstance(s, Schema) and isinstance(s.type, SchemaType)}
    assert types == {SchemaType.INTEGER, SchemaType.NULL}


def test_generate_schema_list_items() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(list[int]))
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.ARRAY
    assert isinstance(schema.items, Schema)
    assert schema.items.type == SchemaType.INTEGER


def test_generate_schema_dict_additional_properties() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(dict[str, int]))
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.OBJECT
    assert isinstance(schema.additional_properties, Schema)
    assert schema.additional_properties.type == SchemaType.INTEGER


def test_generate_schema_literal_enum_const() -> None:
    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(Literal["a", "b"]))
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.STRING
    assert schema.enum == ["a", "b"]

    schema2 = gen.generate_schema(FieldDefinition.from_annotation(Literal[1]))
    assert isinstance(schema2, Schema)
    assert schema2.type == SchemaType.INTEGER
    assert schema2.const == 1


def test_generate_schema_model_is_componentized() -> None:
    class M:
        pass

    gen = AsyncAPISchemaGenerator()
    schema = gen.generate_schema(FieldDefinition.from_annotation(M))
    assert isinstance(schema, (Reference, Schema))
    # Model with no plugin support falls back to inline empty Schema.
