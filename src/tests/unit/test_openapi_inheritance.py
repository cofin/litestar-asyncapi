from copy import deepcopy

from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact, ExternalDocumentation, License, Tag

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import Contact as AsyncAPIContact


def openapi_config(**kwargs: object) -> OpenAPIConfig:
    return OpenAPIConfig(**{
        "title": "Orders API",
        "version": "2.1.0",
        "description": "Order service",
        "contact": Contact(name="Ops", email="ops@example.com", url="https://example.com/ops"),
        "license": License(name="MIT", identifier="MIT", url="https://opensource.org/licenses/MIT"),
        "terms_of_service": "https://example.com/terms",
        "external_docs": ExternalDocumentation(url="https://example.com/docs", description="Guide"),
        "summary": "Orders",
        "tags": [Tag(name="orders")],
        **kwargs,
    })


def test_unset_metadata_is_inherited_from_openapi() -> None:
    plugin = AsyncAPIPlugin()
    app = Litestar(openapi_config=openapi_config(), plugins=[plugin])

    info = plugin.get_asyncapi_schema(app)["info"]

    assert info == {
        "title": "Orders API",
        "version": "2.1.0",
        "description": "Order service",
        "termsOfService": "https://example.com/terms",
        "contact": {"name": "Ops", "url": "https://example.com/ops", "email": "ops@example.com"},
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        "externalDocs": {"url": "https://example.com/docs", "description": "Guide"},
    }


def test_explicit_metadata_wins_over_openapi() -> None:
    app = Litestar(openapi_config=openapi_config())
    config = AsyncAPIConfig(
        title="Events", version="9.0.0", description="Realtime", contact=AsyncAPIContact(name="Realtime team")
    )

    info = AsyncAPIGenerator(app, config).build_schema()["info"]

    assert info["title"] == "Events"
    assert info["version"] == "9.0.0"
    assert info["description"] == "Realtime"
    assert info["contact"] == {"name": "Realtime team"}
    assert info["termsOfService"] == "https://example.com/terms"


def test_inheritance_can_be_disabled() -> None:
    app = Litestar(openapi_config=openapi_config())

    info = AsyncAPIGenerator(app, AsyncAPIConfig(inherit_openapi=False)).build_schema()["info"]

    assert info == {"title": "AsyncAPI", "version": "1.0.0"}


def test_default_openapi_title_is_inherited() -> None:
    info = AsyncAPIGenerator(Litestar(), AsyncAPIConfig()).build_schema()["info"]

    assert info == {"title": "Litestar API", "version": "1.0.0"}


def test_missing_openapi_config_falls_back_to_defaults() -> None:
    app = Litestar(openapi_config=None)

    assert AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()["info"] == {"title": "AsyncAPI", "version": "1.0.0"}


def test_openapi_config_is_read_at_build_time_and_not_mutated() -> None:
    plugin = AsyncAPIPlugin()
    app = Litestar(openapi_config=openapi_config(), plugins=[plugin])
    assert app.openapi_config is not None
    app.openapi_config.title = "Renamed"
    fields = ("components", "security", "servers", "tags", "contact", "license", "external_docs")
    before = {name: deepcopy(getattr(app.openapi_config, name)) for name in fields}

    assert plugin.get_asyncapi_schema(app)["info"]["title"] == "Renamed"
    assert {name: getattr(app.openapi_config, name) for name in fields} == before
