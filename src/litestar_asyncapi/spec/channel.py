from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Channel", "Parameter")


@dataclass(slots=True)
class Parameter(BaseSchemaObject):
    """AsyncAPI 3.0 Parameter object."""

    description: str | None = None
    """Description of the parameter; CommonMark is allowed."""
    enum: list[str] | None = None
    """Allowed values of the parameter."""
    default: str | None = None
    """Value used when none is supplied."""
    examples: list[str] | None = None
    """Example values."""
    location: str | None = None
    """Runtime expression for the parameter's value in a message."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class Channel(BaseSchemaObject):
    """AsyncAPI Channel object."""

    address: str | None = None
    """Transport address, which may contain ``{parameter}`` expressions."""

    title: str | None = None
    """Human-friendly channel title."""
    summary: str | None = None
    """Short summary of the channel."""
    description: str | None = None
    """Longer description of the channel; CommonMark is allowed."""

    messages: "dict[str, Message | Reference] | None" = None
    """Messages that may be sent on the channel, keyed by message key."""
    parameters: "dict[str, Parameter | Reference] | None" = None
    """Parameters for expressions in ``address``."""
    servers: "list[Reference] | None" = None
    """References to the servers that host the channel; all servers when omitted."""

    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific channel bindings."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
