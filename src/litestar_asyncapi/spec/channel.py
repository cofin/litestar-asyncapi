from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Channel", "Parameter")


@dataclass(slots=True)
class Parameter(BaseSchemaObject):
    """AsyncAPI 3.0 Parameter object."""

    description: str | None = None
    enum: list[str] | None = None
    default: str | None = None
    examples: list[str] | None = None
    location: str | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema


@dataclass(slots=True)
class Channel(BaseSchemaObject):
    """AsyncAPI Channel object."""

    address: str

    title: str | None = None
    summary: str | None = None
    description: str | None = None

    messages: "dict[str, Message | Reference] | None" = None
    parameters: "dict[str, Parameter] | None" = None
    servers: "list[Reference] | None" = None

    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None
    bindings: dict[str, Any] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
