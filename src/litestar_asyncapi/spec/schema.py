from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi._draft07 import tuple_item_keywords
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
    """Title of the schema."""
    description: str | None = None
    """Description of the schema; CommonMark is allowed."""
    type: "SchemaType | list[SchemaType] | None" = None
    """JSON type, or a list of types."""
    format: "SchemaFormat | str | None" = None
    """Format hint for the value, such as ``date-time`` or ``uuid``."""

    properties: "dict[str, Schema | Reference] | None" = None
    """Schemas of object properties, keyed by property name."""
    required: list[str] | None = None
    """Names of properties that must be present."""
    additional_properties: "bool | Schema | Reference | None" = None
    """Schema for properties not listed in ``properties``, or whether they are allowed."""

    items: "Schema | Reference | list[Schema | Reference] | None" = None
    """Schema of every array item, or a positional list of item schemas."""
    prefix_items: "list[Schema | Reference] | None" = field(default=None, metadata={"alias": "prefixItems"})
    """Positional item schemas for tuples, serialized as a Draft07 ``items`` array."""
    min_items: int | None = None
    """Minimum array length."""
    max_items: int | None = None
    """Maximum array length."""
    unique_items: bool | None = None
    """Whether array items must be unique."""

    min_length: int | None = None
    """Minimum string length."""
    max_length: int | None = None
    """Maximum string length."""
    pattern: str | None = None
    """Regular expression that strings must match."""

    minimum: float | int | None = None
    """Inclusive lower bound for numbers."""
    maximum: float | int | None = None
    """Inclusive upper bound for numbers."""
    exclusive_minimum: float | int | None = None
    """Exclusive lower bound for numbers."""
    exclusive_maximum: float | int | None = None
    """Exclusive upper bound for numbers."""
    multiple_of: float | int | None = None
    """Number that values must be a multiple of."""

    enum: list[Any] | None = None
    """Allowed values."""
    const: Any = field(default=UNSET, metadata={"nullable": True})
    """Single allowed value; ``None`` is emitted as ``null`` and an unset value is omitted."""

    one_of: "list[Schema | Reference] | None" = None
    """Schemas of which exactly one must match."""
    any_of: "list[Schema | Reference] | None" = None
    """Schemas of which at least one must match."""
    all_of: "list[Schema | Reference] | None" = None
    """Schemas that must all match."""
    not_: "Schema | Reference | None" = field(default=None, metadata={"alias": "not"})
    """Schema that must not match, serialized as ``not``."""

    default: Any = field(default=UNSET, metadata={"nullable": True})
    """Default value; ``None`` is emitted as ``null`` and an unset value is omitted."""
    examples: list[Any] | None = None
    """Example values."""
    example: Any = field(default=UNSET, metadata={"nullable": True})
    """Single example value; ``None`` is emitted as ``null`` and an unset value is omitted."""
    schema_id: str | None = field(default=None, metadata={"alias": "$id"})
    """Schema identifier, serialized as ``$id``."""
    schema_dialect: str | None = field(default=None, metadata={"alias": "$schema"})
    """Schema dialect URI, serialized as ``$schema``."""
    comment: str | None = field(default=None, metadata={"alias": "$comment"})
    """Comment for schema authors, serialized as ``$comment``."""
    definitions: "dict[str, Schema | Reference | bool | dict[str, Any]] | None" = None
    """Local schema definitions for ``$ref`` targets."""
    pattern_properties: "dict[str, Schema | Reference | bool | dict[str, Any]] | None" = None
    """Schemas for properties whose names match a regular expression."""
    dependencies: "dict[str, Schema | Reference | bool | list[str] | dict[str, Any]] | None" = None
    """Property dependencies, as required property names or schemas."""
    property_names: "Schema | Reference | bool | dict[str, Any] | None" = None
    """Schema that every property name must match."""
    min_properties: int | None = None
    """Minimum number of object properties."""
    max_properties: int | None = None
    """Maximum number of object properties."""
    additional_items: "Schema | Reference | bool | dict[str, Any] | None" = None
    """Schema for array items beyond the positional ``items`` list."""
    contains: "Schema | Reference | bool | dict[str, Any] | None" = None
    """Schema that at least one array item must match."""
    if_: "Schema | Reference | bool | dict[str, Any] | None" = field(default=None, metadata={"alias": "if"})
    """Condition schema, serialized as ``if``."""
    then: "Schema | Reference | bool | dict[str, Any] | None" = None
    """Schema applied when ``if`` matches."""
    else_: "Schema | Reference | bool | dict[str, Any] | None" = field(default=None, metadata={"alias": "else"})
    """Schema applied when ``if`` does not match, serialized as ``else``."""
    read_only: bool | None = None
    """Whether the value is managed by the owner and not sent by clients."""
    write_only: bool | None = None
    """Whether the value is sent but never returned."""
    content_encoding: str | None = None
    """Encoding of string content, such as ``base64``."""
    content_media_type: str | None = None
    """Media type of string content."""
    deprecated: bool | None = None
    """Whether the value is deprecated."""
    discriminator: str | None = None
    """Property name that selects the matching schema in a polymorphic payload."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""

    def to_schema(self) -> dict[str, Any]:
        """Serialize the schema with Draft07 tuple keywords.

        ``prefix_items`` becomes a positional ``items`` array and ``items``
        becomes ``additionalItems``, so no ``prefixItems`` reaches the document.

        Returns:
            A dictionary representation of the schema.

        Raises:
            ValueError: If ``items`` and ``additional_items`` are both set beside
                ``prefix_items``, or ``items`` is a list beside ``prefix_items``.
        """
        wire = BaseSchemaObject.to_schema(self)
        if "prefixItems" not in wire:
            return wire
        prefix_items = wire.pop("prefixItems")
        keywords = tuple_item_keywords(prefix_items, wire.get("items"), wire.get("additionalItems"))
        items = wire.pop("items", None)
        if "items" in keywords:
            wire[keywords["items"]] = items
        if "prefixItems" in keywords:
            wire["items"] = prefix_items
        return wire


@dataclass(slots=True)
class MultiFormatSchema(BaseSchemaObject):
    """A schema in an explicitly declared non-native format."""

    schema_format: str
    """Schema format identifier, such as ``application/vnd.apache.avro;version=1.9.0``."""
    schema: Any = field(metadata={"nullable": True})
    """Schema in the declared format."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
