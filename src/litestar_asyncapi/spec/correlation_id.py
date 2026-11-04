from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("CorrelationId",)


@dataclass(slots=True)
class CorrelationId(BaseSchemaObject):
    """Defines how to extract a correlation id from a message."""

    location: str
    """Runtime expression for the correlation id, such as ``$message.header#/correlationId``."""
    description: str | None = None
    """Description of the identifier; CommonMark is allowed."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
