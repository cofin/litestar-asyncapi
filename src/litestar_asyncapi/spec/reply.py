from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.reference import Reference

__all__ = ("Reply", "ReplyAddress")


@dataclass(slots=True)
class ReplyAddress(BaseSchemaObject):
    """Describes the reply address used in request/reply messaging patterns."""

    location: str | None = None
    description: str | None = None


@dataclass(slots=True)
class Reply(BaseSchemaObject):
    """AsyncAPI reply object (minimal scaffolding)."""

    address: "ReplyAddress | Reference | None" = None
    channel: "Reference | None" = None
