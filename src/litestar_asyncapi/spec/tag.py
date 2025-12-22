from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation

__all__ = ("Tag",)


@dataclass(slots=True)
class Tag(BaseSchemaObject):
    """AsyncAPI Tag object."""

    name: str
    description: str | None = None
    external_docs: "ExternalDocumentation | None" = None
    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        # Inline extension keys in output.
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
