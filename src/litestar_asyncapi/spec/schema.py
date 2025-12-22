from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import SchemaFormat, SchemaType
    from litestar_asyncapi.spec.reference import Reference

__all__ = ("Schema",)


@dataclass(slots=True)
class Schema(BaseSchemaObject):
    """A JSON Schema (Draft 07 aligned) used in AsyncAPI message payloads and headers."""

    title: str | None = None
    description: str | None = None
    type: "SchemaType | list[SchemaType] | None" = None
    format: "SchemaFormat | str | None" = None

    # object
    properties: "dict[str, Schema | Reference] | None" = None
    required: list[str] | None = None
    additional_properties: "bool | Schema | Reference | None" = None

    # array
    items: "Schema | Reference | None" = None
    min_items: int | None = None
    max_items: int | None = None
    unique_items: bool | None = None

    # strings
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None

    # numbers
    minimum: float | int | None = None
    maximum: float | int | None = None
    exclusive_minimum: float | int | None = None
    exclusive_maximum: float | int | None = None
    multiple_of: float | int | None = None

    # enums / constants
    enum: list[Any] | None = None
    const: Any | None = None

    # composition
    one_of: "list[Schema | Reference] | None" = None
    any_of: "list[Schema | Reference] | None" = None
    all_of: "list[Schema | Reference] | None" = None
    not_: "Schema | Reference | None" = field(default=None, metadata={"alias": "not"})

    # annotations
    default: Any | None = None
    examples: list[Any] | None = None
