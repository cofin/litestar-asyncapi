from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import OperationAction
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.reply import Reply
    from litestar_asyncapi.spec.security_scheme import SecurityScheme
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Operation", "OperationTrait")


@dataclass(slots=True)
class OperationTrait(BaseSchemaObject):
    """Reusable operation properties."""

    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    bindings: "dict[str, Any] | Reference | None" = None
    security: "list[SecurityScheme | Reference] | None" = None

    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Operation(BaseSchemaObject):
    """AsyncAPI Operation object."""

    action: "OperationAction"
    channel: "Reference"

    title: str | None = None
    summary: str | None = None
    description: str | None = None

    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None

    messages: "list[Message | Reference] | None" = None
    reply: "Reply | Reference | None" = None
    traits: "list[OperationTrait | Reference] | None" = None

    bindings: "dict[str, Any] | Reference | None" = None
    security: "list[SecurityScheme | Reference] | None" = None

    extensions: dict[str, Any] = field(default_factory=dict)
