from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import UNSET, BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.correlation_id import CorrelationId
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.schema import MultiFormatSchema, Schema
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Message", "MessageExample", "MessageTrait")


@dataclass(slots=True)
class MessageExample(BaseSchemaObject):
    """An example message with independently optional headers and payload."""

    headers: dict[str, Any] | None = None
    """Example header values."""
    payload: Any = field(default=UNSET, metadata={"nullable": True})
    """Example payload; ``None`` is emitted as an explicit ``null`` and an unset value is omitted."""
    name: str | None = None
    """Machine-friendly example name."""
    summary: str | None = None
    """Short summary of the example."""


@dataclass(slots=True)
class MessageTrait(BaseSchemaObject):
    """Reusable message properties, excluding payload and traits."""

    name: str | None = None
    """Machine-friendly message name."""
    headers: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    """Schema of the message headers."""
    correlation_id: "CorrelationId | Reference | None" = None
    """Location of the correlation id in the message."""
    content_type: str | None = None
    """Media type of the payload."""
    examples: list[MessageExample] | None = None
    """Example messages."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""

    deprecated: bool | None = None
    """Whether the message is deprecated."""
    title: str | None = None
    """Human-friendly message title."""
    summary: str | None = None
    """Short summary of the message."""
    description: str | None = None
    """Longer description of the message; CommonMark is allowed."""
    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific message bindings."""


@dataclass(slots=True)
class Message(BaseSchemaObject):
    """AsyncAPI Message object."""

    name: str | None = None
    """Machine-friendly message name."""
    deprecated: bool | None = None
    """Whether the message is deprecated."""
    title: str | None = None
    """Human-friendly message title."""
    summary: str | None = None
    """Short summary of the message."""
    description: str | None = None
    """Longer description of the message; CommonMark is allowed."""

    headers: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    """Schema of the message headers."""
    payload: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    """Schema of the message payload."""
    correlation_id: "CorrelationId | Reference | None" = None
    """Location of the correlation id in the message."""
    content_type: str | None = None
    """Media type of the payload; the document's default content type applies when omitted."""

    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""

    traits: "list[MessageTrait | Reference] | None" = None
    """Traits applied to the message."""
    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific message bindings."""
    examples: list[MessageExample] | None = None
    """Example messages."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
