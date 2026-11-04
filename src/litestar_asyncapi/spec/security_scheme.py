from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import SecuritySchemeType

__all__ = ("SecurityScheme",)


@dataclass(slots=True)
class SecurityScheme(BaseSchemaObject):
    """AsyncAPI Security Scheme object."""

    type: "SecuritySchemeType"
    """Type of the security scheme."""

    description: str | None = None
    """Description of the scheme; CommonMark is allowed."""
    name: str | None = None
    """Name of the header, query or cookie parameter for ``httpApiKey`` schemes."""
    in_: str | None = field(default=None, metadata={"alias": "in"})
    """Location of the key, serialized as ``in``: ``user`` or ``password`` for ``apiKey``, ``query``, ``header`` or ``cookie`` for ``httpApiKey``."""
    scopes: list[str] | None = None
    """Scopes required by the operation or server."""
    scheme: str | None = None
    """HTTP authorization scheme for ``http`` schemes, such as ``bearer``."""
    bearer_format: str | None = None
    """Format hint for bearer tokens, such as ``JWT``."""
    open_id_connect_url: str | None = None
    """OpenID Connect discovery URL for ``openIdConnect`` schemes."""

    flows: dict[str, Any] | None = None
    """OAuth2 flow configuration for ``oauth2`` schemes."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
