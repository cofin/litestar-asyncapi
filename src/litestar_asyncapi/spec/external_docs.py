from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("ExternalDocumentation",)


@dataclass(slots=True)
class ExternalDocumentation(BaseSchemaObject):
    """Reference external documentation."""

    url: str
    """URL of the documentation."""
    description: str | None = None
    """Description of the documentation; CommonMark is allowed."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
