from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import OperationAction
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.reply import Reply
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Operation", "OperationTrait")


@dataclass(slots=True)
class OperationTrait(BaseSchemaObject):
    """Reusable operation properties (placeholder for advanced features)."""

    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None
    bindings: dict[str, Any] | None = None
    security: list[dict[str, list[str]]] | None = None


@dataclass(slots=True)
class Operation(BaseSchemaObject):
    """AsyncAPI Operation object."""

    action: "OperationAction"
    channel: "Reference"

    operation_id: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None

    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None

    messages: "list[Message | Reference] | None" = None
    reply: "Reply | Reference | None" = None
    traits: "list[OperationTrait | Reference] | None" = None

    bindings: dict[str, Any] | None = None
    security: list[dict[str, list[str]]] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
