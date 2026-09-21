from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import UNSET, BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.correlation_id import CorrelationId
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.schema import MultiFormatSchema, Schema
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Message", "MessageExample", "MessageTrait")


@dataclass(slots=True)
class MessageExample(BaseSchemaObject):
    """An example message with independently optional headers and payload."""

    headers: dict[str, Any] | None = None
    payload: Any = field(default=UNSET, metadata={"nullable": True})
    name: str | None = None
    summary: str | None = None


@dataclass(slots=True)
class MessageTrait(BaseSchemaObject):
    """Reusable message properties, excluding payload and traits."""

    name: str | None = None
    headers: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    correlation_id: "CorrelationId | Reference | None" = None
    content_type: str | None = None
    examples: list[MessageExample] | None = None
    extensions: dict[str, Any] = field(default_factory=dict)

    deprecated: bool | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    bindings: "dict[str, Any] | Reference | None" = None


@dataclass(slots=True)
class Message(BaseSchemaObject):
    """AsyncAPI Message object."""

    name: str | None = None
    deprecated: bool | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None

    headers: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    payload: "Schema | Reference | MultiFormatSchema | dict[str, Any] | bool | None" = None
    correlation_id: "CorrelationId | Reference | None" = None
    content_type: str | None = None

    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None

    traits: "list[MessageTrait | Reference] | None" = None
    bindings: "dict[str, Any] | Reference | None" = None
    examples: list[MessageExample] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)
