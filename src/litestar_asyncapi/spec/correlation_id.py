from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("CorrelationId",)


@dataclass(slots=True)
class CorrelationId(BaseSchemaObject):
    """Defines how to extract a correlation id from a message."""

    location: str
    description: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
