from enum import Enum
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

from litestar.params import KwargDefinition
from litestar.types import Empty
from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import Reference, Schema, SchemaType

__all__ = (
    "apply_field_constraints",
    "create_literal_schema",
    "is_literal",
    "is_union",
    "split_optional_union",
)


def is_union(annotation: Any) -> bool:
    return get_origin(annotation) in {Union, UnionType}


def is_literal(annotation: Any) -> bool:
    return get_origin(annotation) is Literal


def _schema_type_for_value(value: Any) -> SchemaType:
    if value is None:
        return SchemaType.NULL
    if isinstance(value, bool):
        return SchemaType.BOOLEAN
    if isinstance(value, int):
        return SchemaType.INTEGER
    if isinstance(value, float):
        return SchemaType.NUMBER
    if isinstance(value, str):
        return SchemaType.STRING
    if isinstance(value, bytes):
        return SchemaType.STRING
    if isinstance(value, dict):
        return SchemaType.OBJECT
    if isinstance(value, list):
        return SchemaType.ARRAY
    return SchemaType.STRING


def _iter_flat_literal_args(annotation: Any) -> list[Any]:
    args: list[Any] = []
    for arg in get_args(annotation):
        if get_origin(arg) is Literal:
            args.extend(_iter_flat_literal_args(arg))
        else:
            args.append(arg.value if isinstance(arg, Enum) else arg)
    return args


def create_literal_schema(annotation: Any, *, include_null: bool = False) -> Schema:
    values = _iter_flat_literal_args(annotation)
    if include_null and None not in values:
        values.append(None)

    schema_types = sorted({_schema_type_for_value(v) for v in values}, key=lambda t: t.value)
    schema = Schema(type=schema_types[0] if len(schema_types) == 1 else schema_types)

    if len(values) > 1:
        schema.enum = values
    else:
        schema.const = values[0]

    return schema


def split_optional_union(annotation: Any) -> tuple[list[Any], bool]:
    """Return (non_none_args, is_optional)."""
    args = list(get_args(annotation))
    none_type = type(None)
    is_optional = any(a is none_type for a in args)
    non_none = [a for a in args if a is not none_type]
    return non_none, is_optional


def _schema_allows_type(schema: Schema, allowed: set[SchemaType]) -> bool:
    if schema.type is None:
        return False
    if isinstance(schema.type, list):
        return any(t in allowed for t in schema.type)
    return schema.type in allowed


def _apply_constraints_to_schema(schema: Schema, kwarg_definition: KwargDefinition) -> None:
    if _schema_allows_type(schema, {SchemaType.STRING}):
        if kwarg_definition.min_length is not None:
            schema.min_length = kwarg_definition.min_length
        if kwarg_definition.max_length is not None:
            schema.max_length = kwarg_definition.max_length
        if kwarg_definition.pattern is not None:
            schema.pattern = kwarg_definition.pattern
        if kwarg_definition.format is not None and schema.format is None:
            schema.format = kwarg_definition.format

    if _schema_allows_type(schema, {SchemaType.ARRAY}):
        if kwarg_definition.min_items is not None:
            schema.min_items = kwarg_definition.min_items
        if kwarg_definition.max_items is not None:
            schema.max_items = kwarg_definition.max_items

    if _schema_allows_type(schema, {SchemaType.INTEGER, SchemaType.NUMBER}):
        if kwarg_definition.ge is not None:
            schema.minimum = kwarg_definition.ge
        if kwarg_definition.gt is not None:
            schema.exclusive_minimum = kwarg_definition.gt
        if kwarg_definition.le is not None:
            schema.maximum = kwarg_definition.le
        if kwarg_definition.lt is not None:
            schema.exclusive_maximum = kwarg_definition.lt
        if kwarg_definition.multiple_of is not None:
            schema.multiple_of = kwarg_definition.multiple_of

    if kwarg_definition.enum is not None:
        schema.enum = list(kwarg_definition.enum)

    if kwarg_definition.const and kwarg_definition.default is not Empty:
        schema.const = kwarg_definition.default
    elif kwarg_definition.default is not Empty:
        schema.default = kwarg_definition.default


def _has_supported_constraints(kwarg_definition: KwargDefinition) -> bool:
    return (
        any(
            attr is not None
            for attr in (
                kwarg_definition.gt,
                kwarg_definition.ge,
                kwarg_definition.lt,
                kwarg_definition.le,
                kwarg_definition.multiple_of,
                kwarg_definition.min_items,
                kwarg_definition.max_items,
                kwarg_definition.min_length,
                kwarg_definition.max_length,
                kwarg_definition.pattern,
                kwarg_definition.format,
                kwarg_definition.enum,
            )
        )
        or (kwarg_definition.const and kwarg_definition.default is not Empty)
        or kwarg_definition.default is not Empty
    )


def apply_field_constraints(schema: Schema | Reference, field_definition: FieldDefinition) -> Schema | Reference:
    kwarg_definition = field_definition.kwarg_definition
    if not isinstance(kwarg_definition, KwargDefinition):
        return schema

    if not _has_supported_constraints(kwarg_definition):
        return schema

    if isinstance(schema, Reference):
        wrapper = Schema(all_of=[schema])
        _apply_constraints_to_schema(wrapper, kwarg_definition)
        return wrapper

    _apply_constraints_to_schema(schema, kwarg_definition)
    return schema
