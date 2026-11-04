"""Conversion of the application's Litestar OpenAPI configuration into AsyncAPI objects.

This module is the single place that reads ``app.openapi_config``. It reads the configuration when a
document is built, after auth backends have registered their components, and never mutates it or
asks Litestar to build the OpenAPI schema.
"""

from typing import TYPE_CHECKING

from litestar.openapi.spec import Contact as OpenAPIContact
from litestar.openapi.spec import ExternalDocumentation as OpenAPIExternalDocumentation
from litestar.openapi.spec import License as OpenAPILicense

from litestar_asyncapi.spec import Contact, ExternalDocumentation, Info, License

if TYPE_CHECKING:
    from litestar.openapi import OpenAPIConfig

    from litestar_asyncapi.config import AsyncAPIConfig

__all__ = ("inherited_info",)

DEFAULT_TITLE = "AsyncAPI"
DEFAULT_VERSION = "1.0.0"


def inherited_info(config: "AsyncAPIConfig", openapi: "OpenAPIConfig | None") -> Info:
    """Return document metadata, filling unset fields from the OpenAPI config.

    Explicit ``AsyncAPIConfig`` values win. OpenAPI tags, ``summary`` and ``License.identifier`` have no
    AsyncAPI ``Info`` equivalent and are not carried over.

    Args:
        config: The AsyncAPI configuration.
        openapi: The application's OpenAPI configuration, or ``None`` when absent or not inherited.

    Returns:
        The document ``Info`` object.
    """
    inherited = (
        Info(
            title=openapi.title or DEFAULT_TITLE,
            version=openapi.version or DEFAULT_VERSION,
            description=openapi.description,
            terms_of_service=openapi.terms_of_service,
            contact=_contact(openapi.contact),
            license=_license(openapi.license),
            external_docs=_external_docs(openapi.external_docs),
        )
        if openapi is not None and config.inherit_openapi
        else Info(title=DEFAULT_TITLE, version=DEFAULT_VERSION)
    )
    return Info(
        title=config.title if config.title is not None else inherited.title,
        version=config.version if config.version is not None else inherited.version,
        description=config.description if config.description is not None else inherited.description,
        terms_of_service=(
            config.terms_of_service if config.terms_of_service is not None else inherited.terms_of_service
        ),
        contact=config.contact if config.contact is not None else inherited.contact,
        license=config.license if config.license is not None else inherited.license,
        external_docs=config.external_docs if config.external_docs is not None else inherited.external_docs,
    )


def _contact(value: OpenAPIContact | None) -> Contact | None:
    return Contact(name=value.name, url=value.url, email=value.email) if value is not None else None


def _license(value: OpenAPILicense | None) -> License | None:
    return License(name=value.name, url=value.url) if value is not None else None


def _external_docs(value: OpenAPIExternalDocumentation | None) -> ExternalDocumentation | None:
    return ExternalDocumentation(url=value.url, description=value.description) if value is not None else None
