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
    """Value used when none is supplied."""
    enum: list[str] | None = None
    """Allowed values of the variable."""
    description: str | None = None
    """Description of the variable; CommonMark is allowed."""
    examples: list[str] | None = None
    """Example values."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class Server(BaseSchemaObject):
    """AsyncAPI Server object."""

    host: str
    """Host name, which may include a port and ``{variable}`` expressions."""
    protocol: str
    """Protocol used to connect, such as ``ws``, ``wss`` or ``kafka``."""

    title: str | None = None
    """Human-friendly server title."""
    summary: str | None = None
    """Short summary of the server."""
    protocol_version: str | None = None
    """Version of the protocol."""
    pathname: str | None = None
    """Path relative to the host, which may include ``{variable}`` expressions."""
    description: str | None = None
    """Description of the server; CommonMark is allowed."""

    variables: "dict[str, ServerVariable | Reference] | None" = None
    """Variables for expressions in ``host`` and ``pathname``."""

    security: "list[SecurityScheme | Reference] | None" = None
    """Security schemes that apply to connections to the server."""
    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    bindings: "dict[str, Any] | Reference | None" = None
    """Protocol-specific server bindings."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
