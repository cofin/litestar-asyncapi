from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Contact", "Info", "License")


@dataclass(slots=True)
class Contact(BaseSchemaObject):
    """Contact information for the exposed API."""

    name: str | None = None
    url: str | None = None
    email: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class License(BaseSchemaObject):
    """License information for the exposed API."""

    name: str
    url: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Info(BaseSchemaObject):
    """Information about the exposed API."""

    title: str
    version: str
    description: str | None = None
    terms_of_service: str | None = None
    contact: Contact | None = None
    license: License | None = None
    tags: "list[Tag | Reference] | None" = None
    external_docs: "ExternalDocumentation | Reference | None" = None
    extensions: dict[str, Any] = field(default_factory=dict)
