from collections.abc import Mapping as AbcMapping
from collections.abc import MutableMapping as AbcMutableMapping
from collections.abc import Sequence
from collections.abc import Sequence as AbcSequence
from copy import copy
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network
from pathlib import Path
from re import Pattern
from types import UnionType
from typing import TYPE_CHECKING, Any, Literal, Union, cast, get_args, get_origin
from uuid import UUID

from litestar.types.builtin_types import NoneType
from litestar.typing import FieldDefinition
from litestar.utils.predicates import is_class_and_subclass, is_optional_union
from litestar.utils.typing import make_non_optional_union

from litestar_asyncapi.asyncapi.datastructures import SchemaRegistry
from litestar_asyncapi.asyncapi.schema_generation.plugins.attrs import AttrsSchemaPlugin
from litestar_asyncapi.asyncapi.schema_generation.plugins.dataclass import DataclassSchemaPlugin
from litestar_asyncapi.asyncapi.schema_generation.plugins.msgspec import MsgspecSchemaPlugin
from litestar_asyncapi.asyncapi.schema_generation.plugins.pydantic import PydanticSchemaPlugin
from litestar_asyncapi.asyncapi.schema_generation.plugins.typed_dict import TypedDictSchemaPlugin
from litestar_asyncapi.asyncapi.schema_generation.utils import (
    apply_field_constraints,
    create_literal_schema,
)
from litestar_asyncapi.spec import Reference, Schema, SchemaFormat, SchemaType

if TYPE_CHECKING:
    from litestar_asyncapi.asyncapi.schema_generation.plugins import AsyncAPISchemaPluginProtocol

__all__ = ("AsyncAPISchemaGenerator",)


TYPE_MAP: dict[Any, Schema] = {
    Decimal: Schema(type=SchemaType.NUMBER),
    IPv4Address: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV4),
    IPv4Interface: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV4),
    IPv4Network: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV4),
    IPv6Address: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV6),
    IPv6Interface: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV6),
    IPv6Network: Schema(type=SchemaType.STRING, format=SchemaFormat.IPV6),
    AbcMapping: Schema(type=SchemaType.OBJECT),
    AbcMutableMapping: Schema(type=SchemaType.OBJECT),
    None: Schema(type=SchemaType.NULL),
    NoneType: Schema(type=SchemaType.NULL),
    Path: Schema(type=SchemaType.STRING, format=SchemaFormat.URI),
    Pattern: Schema(type=SchemaType.STRING, format=SchemaFormat.REGEX),
    UUID: Schema(type=SchemaType.STRING, format=SchemaFormat.UUID),
    bool: Schema(type=SchemaType.BOOLEAN),
    bytes: Schema(type=SchemaType.STRING),
    bytearray: Schema(type=SchemaType.STRING),
    date: Schema(type=SchemaType.STRING, format=SchemaFormat.DATE),
    datetime: Schema(type=SchemaType.STRING, format=SchemaFormat.DATE_TIME),
    float: Schema(type=SchemaType.NUMBER),
    int: Schema(type=SchemaType.INTEGER),
    list: Schema(type=SchemaType.ARRAY),
    dict: Schema(type=SchemaType.OBJECT),
    set: Schema(type=SchemaType.ARRAY),
    str: Schema(type=SchemaType.STRING),
    time: Schema(type=SchemaType.STRING, format=SchemaFormat.DURATION),
    timedelta: Schema(type=SchemaType.STRING, format=SchemaFormat.DURATION),
    tuple: Schema(type=SchemaType.ARRAY),
}


class AsyncAPISchemaGenerator:
    __slots__ = ("plugins", "schema_registry")

    def __init__(self, *, plugins: "Sequence[AsyncAPISchemaPluginProtocol] | None" = None) -> None:
        self.schema_registry = SchemaRegistry()
        self.plugins: "list[AsyncAPISchemaPluginProtocol]" = list(
            plugins
            if plugins is not None
            else (
                PydanticSchemaPlugin(),
                AttrsSchemaPlugin(),
                DataclassSchemaPlugin(),
                MsgspecSchemaPlugin(),
                TypedDictSchemaPlugin(),
            )
        )

    @staticmethod
    def _schema_for_annotation(annotation: Any) -> Schema:
        return copy(TYPE_MAP[annotation]) if annotation in TYPE_MAP else Schema()

    def generate_schema(self, field_definition: FieldDefinition) -> Schema | Reference:
        annotation = field_definition.annotation
        origin = get_origin(annotation)

        if origin is Literal:
            return apply_field_constraints(create_literal_schema(annotation), field_definition)

        if origin is tuple:
            return self._generate_tuple_schema(field_definition)

        if origin in {list, set, AbcSequence}:
            return self._generate_list_schema(field_definition)

        if origin in {dict, AbcMapping, AbcMutableMapping}:
            return self._generate_mapping_schema(field_definition)

        # Union / Optional
        if origin in {Union, UnionType}:
            return self._generate_union_schema(field_definition)

        if annotation in TYPE_MAP:
            return apply_field_constraints(self._schema_for_annotation(annotation), field_definition)

        if is_class_and_subclass(annotation, Enum):
            return self._generate_enum_schema(annotation, field_definition)

        for plugin in self.plugins:
            if plugin.supports(field_definition):
                # Always componentize supported "model" types.
                component_schema = self.schema_registry.get_schema_for_field_definition(field_definition)
                plugin.populate_component_schema(
                    schema=component_schema, field_definition=field_definition, generator=self
                )
                reference = self.schema_registry.get_reference_for_field_definition(field_definition)
                if reference is None:
                    return apply_field_constraints(Schema(), field_definition)
                return cast("Reference", apply_field_constraints(reference, field_definition))

        return apply_field_constraints(Schema(), field_definition)

    def _generate_tuple_schema(self, field_definition: FieldDefinition) -> Schema:
        args = get_args(field_definition.annotation)
        if not args:
            return cast("Schema", apply_field_constraints(Schema(type=SchemaType.ARRAY), field_definition))
        if len(args) == 2 and args[1] is Ellipsis:
            items = self.generate_schema(FieldDefinition.from_annotation(args[0]))
            return cast("Schema", apply_field_constraints(Schema(type=SchemaType.ARRAY, items=items), field_definition))

        prefix_items = [self.generate_schema(FieldDefinition.from_annotation(arg)) for arg in args]
        schema = Schema(
            type=SchemaType.ARRAY,
            prefix_items=prefix_items,
            min_items=len(args),
            max_items=len(args),
        )
        return cast("Schema", apply_field_constraints(schema, field_definition))

    def _generate_list_schema(self, field_definition: FieldDefinition) -> Schema:
        args = get_args(field_definition.annotation)
        items = self.generate_schema(FieldDefinition.from_annotation(args[0])) if args else Schema()
        return cast("Schema", apply_field_constraints(Schema(type=SchemaType.ARRAY, items=items), field_definition))

    def _generate_mapping_schema(self, field_definition: FieldDefinition) -> Schema:
        args = get_args(field_definition.annotation)
        value_type = args[1] if len(args) == 2 else Any
        additional = self.generate_schema(FieldDefinition.from_annotation(value_type))
        return cast(
            "Schema",
            apply_field_constraints(
                Schema(type=SchemaType.OBJECT, additional_properties=additional),
                field_definition,
            ),
        )

    def _generate_union_schema(self, field_definition: FieldDefinition) -> Schema | Reference:
        annotation = field_definition.annotation
        is_optional = is_optional_union(annotation)
        non_optional_annotation = make_non_optional_union(annotation)

        if get_origin(non_optional_annotation) in {Union, UnionType}:
            union_args = get_args(non_optional_annotation)
        else:
            union_args = (non_optional_annotation,)

        schemas = [self.generate_schema(FieldDefinition.from_annotation(a)) for a in union_args]
        if is_optional:
            schemas.append(Schema(type=SchemaType.NULL))
        if len(schemas) == 1:
            return apply_field_constraints(schemas[0], field_definition)
        return apply_field_constraints(Schema(one_of=schemas), field_definition)

    @staticmethod
    def _generate_enum_schema(annotation: Any, field_definition: FieldDefinition) -> Schema:
        values = [e.value for e in annotation]
        schema_types = sorted({_schema_type_for_enum_value(v) for v in values}, key=lambda t: t.value)
        schema = Schema(type=schema_types[0] if len(schema_types) == 1 else schema_types)
        schema.enum = values
        return apply_field_constraints(schema, field_definition)


def _schema_type_for_enum_value(value: Any) -> SchemaType:
    if value is None:
        return SchemaType.NULL
    if isinstance(value, bool):
        return SchemaType.BOOLEAN
    if isinstance(value, int):
        return SchemaType.INTEGER
    if isinstance(value, float):
        return SchemaType.NUMBER
    return SchemaType.STRING
