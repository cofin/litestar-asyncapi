from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import OperationAction
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.reply import Reply
    from litestar_asyncapi.spec.security_scheme import SecurityScheme
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Operation", "OperationTrait")


@dataclass(slots=True)
class OperationTrait(BaseSchemaObject):
    """Reusable operation properties."""

    title: str | None = None
    """Human-friendly operation title."""
    summary: str | None = None
    """Short summary of the operation."""
    description: str | None = None
    """Longer description of the operation; CommonMark is allowed."""
    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific operation bindings."""
    security: "list[SecurityScheme | Reference] | None" = None
    """Security schemes that apply to the operation."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class Operation(BaseSchemaObject):
    """AsyncAPI Operation object."""

    action: "OperationAction"
    """Direction from the application's perspective: ``send`` or ``receive``."""
    channel: "Reference"
    """Reference to the channel the operation acts on."""

    title: str | None = None
    """Human-friendly operation title."""
    summary: str | None = None
    """Short summary of the operation."""
    description: str | None = None
    """Longer description of the operation; CommonMark is allowed."""

    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""

    messages: "list[Message | Reference] | None" = None
    """References to the channel messages the operation carries; all of them when omitted."""
    reply: "Reply | Reference | None" = None
    """Reply that the operation expects, for request and reply patterns."""
    traits: "list[OperationTrait | Reference] | None" = None
    """Traits applied to the operation."""

    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific operation bindings."""
    security: "list[SecurityScheme | Reference] | None" = None
    """Security schemes that apply to the operation."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
