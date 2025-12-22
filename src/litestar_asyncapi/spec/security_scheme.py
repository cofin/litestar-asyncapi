from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.enums import SecuritySchemeType

__all__ = ("SecurityScheme",)


@dataclass(slots=True)
class SecurityScheme(BaseSchemaObject):
    """AsyncAPI Security Scheme object (subset required for initial support)."""

    type: "SecuritySchemeType"

    description: str | None = None
    name: str | None = None
    in_: str | None = None
    scheme: str | None = None
    bearer_format: str | None = None
    open_id_connect_url: str | None = None

    # OAuth2 details are left flexible for now (PRD-006 can tighten this).
    flows: dict[str, Any] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
