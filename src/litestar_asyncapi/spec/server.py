from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Server", "ServerVariable")


@dataclass(slots=True)
class ServerVariable(BaseSchemaObject):
    """Server variable for templated server URLs/hosts."""

    default: str
    enum: list[str] | None = None
    description: str | None = None
    examples: list[str] | None = None


@dataclass(slots=True)
class Server(BaseSchemaObject):
    """AsyncAPI Server object."""

    host: str
    protocol: str

    protocol_version: str | None = None
    pathname: str | None = None
    description: str | None = None

    variables: dict[str, ServerVariable] | None = None

    security: list[dict[str, list[str]]] | None = None
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
