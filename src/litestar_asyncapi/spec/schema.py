from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import UNSET, BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import SchemaFormat, SchemaType
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference

__all__ = ("MultiFormatSchema", "Schema")


@dataclass(slots=True)
class Schema(BaseSchemaObject):
    """A JSON Schema (Draft 07 aligned) used in AsyncAPI message payloads and headers."""

    title: str | None = None
    description: str | None = None
    type: "SchemaType | list[SchemaType] | None" = None
    format: "SchemaFormat | str | None" = None

    properties: "dict[str, Schema | Reference] | None" = None
    required: list[str] | None = None
    additional_properties: "bool | Schema | Reference | None" = None

    items: "Schema | Reference | None" = None
    prefix_items: "list[Schema | Reference] | None" = field(default=None, metadata={"alias": "prefixItems"})
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None

    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None

    minimum: float | int | None = None
    maximum: float | int | None = None
    exclusive_minimum: float | int | None = None
    exclusive_maximum: float | int | None = None
    multiple_of: float | int | None = None

    enum: list[Any] | None = None
    const: Any = field(default=UNSET, metadata={"nullable": True})

    one_of: "list[Schema | Reference] | None" = None
    any_of: "list[Schema | Reference] | None" = None
    all_of: "list[Schema | Reference] | None" = None
    not_: "Schema | Reference | None" = field(default=None, metadata={"alias": "not"})

    default: Any = field(default=UNSET, metadata={"nullable": True})
    examples: list[Any] | None = None
    example: Any = field(default=UNSET, metadata={"nullable": True})
    schema_id: str | None = field(default=None, metadata={"alias": "$id"})
    schema_dialect: str | None = field(default=None, metadata={"alias": "$schema"})
    comment: str | None = field(default=None, metadata={"alias": "$comment"})
    definitions: "dict[str, Schema | Reference | bool | dict[str, Any]] | None" = None
    pattern_properties: "dict[str, Schema | Reference | bool | dict[str, Any]] | None" = None
    dependencies: "dict[str, Schema | Reference | bool | list[str] | dict[str, Any]] | None" = None
    property_names: "Schema | Reference | bool | dict[str, Any] | None" = None
    min_properties: int | None = None
    max_properties: int | None = None
    additional_items: "Schema | Reference | bool | dict[str, Any] | None" = None
    contains: "Schema | Reference | bool | dict[str, Any] | None" = None
    if_: "Schema | Reference | bool | dict[str, Any] | None" = field(default=None, metadata={"alias": "if"})
    then: "Schema | Reference | bool | dict[str, Any] | None" = None
    else_: "Schema | Reference | bool | dict[str, Any] | None" = field(default=None, metadata={"alias": "else"})
    read_only: bool | None = None
    write_only: bool | None = None
    content_encoding: str | None = None
    content_media_type: str | None = None
    deprecated: bool | None = None
    discriminator: str | None = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MultiFormatSchema(BaseSchemaObject):
    """A schema in an explicitly declared non-native format."""

    schema_format: str
    schema: Any = field(metadata={"nullable": True})
    extensions: dict[str, Any] = field(default_factory=dict)
