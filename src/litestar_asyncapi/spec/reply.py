from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.reference import Reference

__all__ = ("Reply", "ReplyAddress")


@dataclass(slots=True)
class ReplyAddress(BaseSchemaObject):
    """Describes the reply address used in request/reply messaging patterns."""

    location: str
    """Runtime expression for the reply address, such as ``$message.header#/replyTo``."""
    description: str | None = None
    """Description of the address; CommonMark is allowed."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class Reply(BaseSchemaObject):
    """AsyncAPI Reply object for request and reply patterns."""

    address: "ReplyAddress | Reference | None" = None
    """Where the reply is sent when it is not a fixed channel address."""
    channel: "Reference | None" = None
    """Reference to the channel the reply is sent on."""
    messages: "list[Reference] | None" = None
    """References to the messages that may be sent as the reply."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
