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
    """Name of the contact person or organization."""
    url: str | None = None
    """URL with contact information."""
    email: str | None = None
    """Email address of the contact."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class License(BaseSchemaObject):
    """License information for the exposed API."""

    name: str
    """Name of the license."""
    url: str | None = None
    """URL of the license text."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class Info(BaseSchemaObject):
    """Information about the exposed API."""

    title: str
    """Title of the application."""
    version: str
    """Version of the application API, not of the AsyncAPI specification."""
    description: str | None = None
    """Description of the application; CommonMark is allowed."""
    terms_of_service: str | None = None
    """URL of the terms of service."""
    contact: Contact | None = None
    """Contact information for the API."""
    license: License | None = None
    """License of the API."""
    tags: "list[Tag | Reference] | None" = None
    """Tags for logical grouping."""
    external_docs: "ExternalDocumentation | Reference | None" = None
    """Additional external documentation."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
