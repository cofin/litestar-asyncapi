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
    description: str | None = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    extensions: dict[str, Any] = field(default_factory=dict)
