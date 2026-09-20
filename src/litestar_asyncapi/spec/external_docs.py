from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("ExternalDocumentation",)


@dataclass(slots=True)
class ExternalDocumentation(BaseSchemaObject):
    """Reference external documentation."""

    url: str
    description: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
