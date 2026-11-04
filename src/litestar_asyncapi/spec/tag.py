from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference

__all__ = ("Tag",)


@dataclass(slots=True)
class Tag(BaseSchemaObject):
    """AsyncAPI Tag object."""

    name: str
    """Name of the tag."""
    description: str | None = None
    """Description of the tag; CommonMark is allowed."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
