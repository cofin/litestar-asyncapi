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
    description: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Reply(BaseSchemaObject):
    """AsyncAPI reply object (minimal scaffolding)."""

    address: "ReplyAddress | Reference | None" = None
    channel: "Reference | None" = None
    messages: "list[Reference] | None" = None
    extensions: dict[str, Any] = field(default_factory=dict)
