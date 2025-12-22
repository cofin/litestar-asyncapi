from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.correlation_id import CorrelationId
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.schema import Schema
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Message", "MessageTrait")


@dataclass(slots=True)
class MessageTrait(BaseSchemaObject):
    """Reusable message properties (placeholder for advanced features)."""

    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None
    bindings: dict[str, Any] | None = None


@dataclass(slots=True)
class Message(BaseSchemaObject):
    """AsyncAPI Message object."""

    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None

    headers: "Schema | Reference | None" = None
    payload: "Schema | Reference | None" = None
    correlation_id: "CorrelationId | Reference | None" = None
    content_type: str | None = None

    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None

    traits: "list[MessageTrait | Reference] | None" = None
    bindings: dict[str, Any] | None = None
    examples: list[Any] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
