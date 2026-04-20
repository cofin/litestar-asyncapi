from typing import Any, Literal
from litestar.params import KwargDefinition
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation.utils import (
    _schema_type_for_value,
    apply_field_constraints,
    create_literal_schema,
)
from litestar_asyncapi.spec import Schema, SchemaType


def test_schema_type_for_value() -> None:
    assert _schema_type_for_value(None) == SchemaType.NULL
    assert _schema_type_for_value(True) == SchemaType.BOOLEAN
    assert _schema_type_for_value(1) == SchemaType.INTEGER
    assert _schema_type_for_value(1.1) == SchemaType.NUMBER
    assert _schema_type_for_value("a") == SchemaType.STRING
    assert _schema_type_for_value([]) == SchemaType.ARRAY
    assert _schema_type_for_value({}) == SchemaType.OBJECT


def test_create_literal_schema() -> None:
    schema = create_literal_schema(Literal["a", 1])
    assert set(schema.type) == {SchemaType.STRING, SchemaType.INTEGER}
    assert set(schema.enum) == {"a", 1}


def test_apply_field_constraints_comprehensive() -> None:
    from dataclasses import replace
    from litestar.params import KwargDefinition
    
    schema = Schema()
    field = FieldDefinition.from_annotation(Any)
    
    kwarg = KwargDefinition(
        title="Title",
        description="Desc",
        default="def",
        enum=["a", "b"],
        const=True,
        examples=["ex"],
        gt=0,
        le=10,
        lt=11,
        multiple_of=2,
        min_items=1,
        max_items=5,
        min_length=2,
        max_length=20,
        pattern=".*",
    )
    field = replace(field, kwarg_definition=kwarg)
    
    updated = apply_field_constraints(schema, field)
    assert updated.title == "Title"
    assert updated.description == "Desc"
    assert updated.const == "def"
    assert updated.default is None
    assert updated.exclusive_minimum == 0
    assert updated.maximum == 10
    assert updated.exclusive_maximum == 11
    assert updated.multiple_of == 2
    assert updated.min_items == 1
    assert updated.max_items == 5
    assert updated.min_length == 2
    assert updated.max_length == 20
    assert updated.pattern == ".*"


def test_apply_field_constraints_list_types() -> None:
    from dataclasses import replace
    from litestar.params import KwargDefinition
    
    schema = Schema(type=[SchemaType.STRING, SchemaType.INTEGER])
    field = replace(FieldDefinition.from_annotation(Any), kwarg_definition=KwargDefinition(min_length=5, ge=1))
    
    updated = apply_field_constraints(schema, field)
    assert updated.min_length == 5
    assert updated.minimum == 1


def test_apply_field_constraints_reference() -> None:
    from litestar_asyncapi.spec import Reference
    from dataclasses import replace
    from litestar.params import KwargDefinition
    
    ref = Reference(ref="#/components/schemas/User")
    field = replace(FieldDefinition.from_annotation(Any), kwarg_definition=KwargDefinition(title="Title"))
    
    updated = apply_field_constraints(ref, field)
    assert isinstance(updated, Schema)
    assert updated.all_of is not None
    assert updated.all_of[0] == ref
    assert updated.title == "Title"
