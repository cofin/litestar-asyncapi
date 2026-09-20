from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.security_scheme import SecurityScheme
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Server", "ServerVariable")


@dataclass(slots=True)
class ServerVariable(BaseSchemaObject):
    """Server variable for templated server URLs/hosts."""

    default: str | None = None
    enum: list[str] | None = None
    description: str | None = None
    examples: list[str] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Server(BaseSchemaObject):
    """AsyncAPI Server object."""

    host: str
    protocol: str

    title: str | None = None
    summary: str | None = None
    protocol_version: str | None = None
    pathname: str | None = None
    description: str | None = None

    variables: "dict[str, ServerVariable | Reference] | None" = None

    security: "list[SecurityScheme | Reference] | None" = None
    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    bindings: "dict[str, Any] | Reference | None" = None

    extensions: dict[str, Any] = field(default_factory=dict)
