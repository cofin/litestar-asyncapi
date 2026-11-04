"""Conversion of the application's Litestar OpenAPI configuration into AsyncAPI objects.

This module is the single place that reads ``app.openapi_config``. It reads the configuration when a
document is built, after auth backends have registered their components, and never mutates it or
asks Litestar to build the OpenAPI schema.
"""

import warnings
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from litestar.openapi.spec import Contact as OpenAPIContact
from litestar.openapi.spec import ExternalDocumentation as OpenAPIExternalDocumentation
from litestar.openapi.spec import License as OpenAPILicense
from litestar.openapi.spec import OAuthFlow, OAuthFlows
from litestar.openapi.spec import SecurityScheme as OpenAPISecurityScheme

from litestar_asyncapi.spec import Contact, ExternalDocumentation, Info, License, SecurityScheme, SecuritySchemeType

if TYPE_CHECKING:
    from litestar.openapi import OpenAPIConfig

    from litestar_asyncapi.config import AsyncAPIConfig

__all__ = ("OPENAPI_SOURCE", "inherited_info", "inherited_security_schemes")

OPENAPI_SOURCE = "OpenAPIConfig.components (inherited)"
"""Source named in errors about inherited components."""

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


def inherited_security_schemes(openapi: "OpenAPIConfig | None") -> dict[str, SecurityScheme]:
    """Return the OpenAPI security scheme definitions converted to AsyncAPI.

    A ``components`` list is merged in order, later entries winning, without changing the config.
    Security requirements are not converted. A scheme or OAuth flow that AsyncAPI cannot express
    is skipped with a ``UserWarning``:

    - ``http`` keeps its scheme in lowercase; bearer schemes keep ``bearerFormat`` and drop ``name``.
    - ``apiKey`` in a header, query or cookie becomes ``httpApiKey``.
    - ``oauth2`` keeps flows whose URLs are absolute, with ``availableScopes`` always present.
    - ``openIdConnect`` is kept and ``mutualTLS`` becomes ``X509``.

    Args:
        openapi: The application's OpenAPI configuration, or ``None``.

    Returns:
        Converted schemes keyed by their OpenAPI name.
    """
    if openapi is None:
        return {}
    components = openapi.components if isinstance(openapi.components, list) else [openapi.components]
    schemes: dict[str, Any] = {}
    for component in components:
        schemes.update(component.security_schemes or {})
    converted = {name: _security_scheme(name, scheme) for name, scheme in schemes.items()}
    return {name: scheme for name, scheme in converted.items() if scheme is not None}


def _security_scheme(name: str, scheme: object) -> SecurityScheme | None:
    if isinstance(scheme, OpenAPISecurityScheme) and (fields := _security_scheme_fields(name, scheme)) is not None:
        return SecurityScheme(description=scheme.description, **fields)
    warnings.warn(f"Skipping OpenAPI security scheme {name!r}: AsyncAPI cannot express it", UserWarning, stacklevel=2)
    return None


def _security_scheme_fields(name: str, scheme: OpenAPISecurityScheme) -> dict[str, Any] | None:
    fields: dict[str, Any] | None = None
    if scheme.type == "http" and scheme.scheme:
        http_scheme = scheme.scheme.lower()
        fields = {"type": SecuritySchemeType.HTTP, "scheme": http_scheme}
        if http_scheme == "bearer":
            fields["bearer_format"] = scheme.bearer_format
    elif scheme.type == "apiKey" and scheme.name and scheme.security_scheme_in in {"header", "query", "cookie"}:
        fields = {"type": SecuritySchemeType.HTTP_API_KEY, "name": scheme.name, "in_": scheme.security_scheme_in}
    elif scheme.type == "openIdConnect" and scheme.open_id_connect_url:
        fields = {"type": SecuritySchemeType.OPEN_ID_CONNECT, "open_id_connect_url": scheme.open_id_connect_url}
    elif scheme.type == "mutualTLS":
        fields = {"type": SecuritySchemeType.X509}
    elif scheme.type == "oauth2" and scheme.flows is not None:
        flows = _oauth_flows(name, scheme.flows)
        fields = {"type": SecuritySchemeType.OAUTH2, "flows": flows} if flows else None
    return fields


def _oauth_flows(name: str, flows: OAuthFlows) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for attribute, key in (
        ("implicit", "implicit"),
        ("password", "password"),
        ("client_credentials", "clientCredentials"),
        ("authorization_code", "authorizationCode"),
    ):
        flow: OAuthFlow | None = getattr(flows, attribute)
        if flow is None:
            continue
        urls = {"authorizationUrl": flow.authorization_url, "tokenUrl": flow.token_url, "refreshUrl": flow.refresh_url}
        if any(url is not None and not _is_absolute(url) for url in urls.values()):
            warnings.warn(
                f"Skipping OpenAPI security scheme {name!r} OAuth flow {attribute!r}: AsyncAPI requires absolute URLs, "
                "not relative ones",
                UserWarning,
                stacklevel=2,
            )
            continue
        converted[key] = {
            **{field: url for field, url in urls.items() if url is not None},
            "availableScopes": dict(flow.scopes or {}),
        }
    return converted


def _is_absolute(url: str) -> bool:
    parts = urlsplit(url)
    return bool(parts.scheme and parts.netloc)
