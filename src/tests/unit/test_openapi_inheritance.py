from copy import deepcopy

import pytest
from litestar import Litestar, get, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import (
    Components,
    Contact,
    ExternalDocumentation,
    License,
    OAuthFlow,
    OAuthFlows,
    Reference,
    SecurityScheme,
    Server,
    ServerVariable,
    Tag,
)
from litestar.response import ServerSentEvent
from litestar.security.jwt import JWTAuth

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
from litestar_asyncapi.spec import Components as AsyncAPIComponents
from litestar_asyncapi.spec import Contact as AsyncAPIContact
from litestar_asyncapi.spec import SecurityScheme as AsyncAPISecurityScheme
from litestar_asyncapi.spec import Server as AsyncAPIServer


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


def security_schemes(*schemes: tuple[str, SecurityScheme], **config: object) -> dict[str, object]:
    app = Litestar(openapi_config=openapi_config(components=Components(security_schemes=dict(schemes))))
    return AsyncAPIGenerator(app, AsyncAPIConfig(**config)).build_schema()["components"].get("securitySchemes", {})


def test_jwt_auth_scheme_is_inherited_as_lowercase_bearer() -> None:
    auth = JWTAuth[object](retrieve_user_handler=lambda token, connection: None, token_secret="x" * 32)
    plugin = AsyncAPIPlugin()
    app = Litestar(on_app_init=[auth.on_app_init], plugins=[plugin])

    document = plugin.get_asyncapi_schema(app)

    assert document["components"]["securitySchemes"] == {
        "BearerToken": {
            "type": "http",
            "description": "JWT api-key authentication and authorization.",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    assert all("security" not in operation for operation in document["operations"].values())


@pytest.mark.parametrize(
    ("scheme", "expected"),
    [
        (SecurityScheme(type="http", scheme="Basic"), {"type": "http", "scheme": "basic"}),
        (
            SecurityScheme(type="apiKey", name="X-Key", security_scheme_in="header", description="Key"),
            {"type": "httpApiKey", "name": "X-Key", "in": "header", "description": "Key"},
        ),
        (
            SecurityScheme(type="apiKey", name="key", security_scheme_in="query"),
            {"type": "httpApiKey", "name": "key", "in": "query"},
        ),
        (
            SecurityScheme(type="apiKey", name="session", security_scheme_in="cookie"),
            {"type": "httpApiKey", "name": "session", "in": "cookie"},
        ),
        (
            SecurityScheme(type="openIdConnect", open_id_connect_url="https://id.example.com/.well-known"),
            {"type": "openIdConnect", "openIdConnectUrl": "https://id.example.com/.well-known"},
        ),
        (
            SecurityScheme(type="mutualTLS", description="Client certificate"),
            {"type": "X509", "description": "Client certificate"},
        ),
        (
            SecurityScheme(
                type="oauth2",
                flows=OAuthFlows(
                    client_credentials=OAuthFlow(token_url="https://id.example.com/token"),
                    authorization_code=OAuthFlow(
                        authorization_url="https://id.example.com/authorize",
                        token_url="https://id.example.com/token",
                        refresh_url="https://id.example.com/refresh",
                        scopes={"orders:read": "Read orders"},
                    ),
                ),
            ),
            {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {"tokenUrl": "https://id.example.com/token", "availableScopes": {}},
                    "authorizationCode": {
                        "authorizationUrl": "https://id.example.com/authorize",
                        "tokenUrl": "https://id.example.com/token",
                        "refreshUrl": "https://id.example.com/refresh",
                        "availableScopes": {"orders:read": "Read orders"},
                    },
                },
            },
        ),
    ],
)
def test_openapi_security_schemes_are_mapped(scheme: SecurityScheme, expected: dict[str, object]) -> None:
    assert security_schemes(("auth", scheme)) == {"auth": expected}


def test_relative_oauth_flows_are_skipped_with_a_warning() -> None:
    scheme = SecurityScheme(
        type="oauth2",
        flows=OAuthFlows(
            password=OAuthFlow(token_url="/token"),
            client_credentials=OAuthFlow(token_url="https://id.example.com/token"),
        ),
    )
    with pytest.warns(UserWarning, match=r"'auth'.*password.*relative"):
        schemes = security_schemes(("auth", scheme))

    assert schemes == {
        "auth": {
            "type": "oauth2",
            "flows": {"clientCredentials": {"tokenUrl": "https://id.example.com/token", "availableScopes": {}}},
        }
    }


@pytest.mark.parametrize(
    "scheme",
    [
        SecurityScheme(type="oauth2", flows=OAuthFlows(implicit=OAuthFlow(authorization_url="/authorize"))),
        SecurityScheme(type="apiKey", name="key"),
        SecurityScheme(type="http"),
        Reference(ref="#/components/securitySchemes/other"),
    ],
)
def test_unmappable_security_schemes_are_skipped_with_a_warning(scheme: SecurityScheme | Reference) -> None:
    with pytest.warns(UserWarning, match="Skipping OpenAPI security scheme 'auth'"):
        assert security_schemes(("auth", scheme)) == {}


def test_list_components_are_merged_without_mutation() -> None:
    first = Components(security_schemes={"key": SecurityScheme(type="apiKey", name="a", security_scheme_in="header")})
    second = Components(security_schemes={"key": SecurityScheme(type="apiKey", name="b", security_scheme_in="query")})
    app = Litestar(openapi_config=openapi_config(components=[first, second]))

    schemes = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()["components"]["securitySchemes"]

    assert schemes == {"key": {"type": "httpApiKey", "name": "b", "in": "query"}}
    assert app.openapi_config is not None
    assert app.openapi_config.components == [first, second]


def test_security_schemes_are_not_inherited_when_disabled() -> None:
    scheme = SecurityScheme(type="http", scheme="basic")

    assert security_schemes(("auth", scheme), inherit_openapi=False) == {}


def test_identical_configured_scheme_is_accepted() -> None:
    configured = AsyncAPIComponents(security_schemes={"auth": AsyncAPISecurityScheme(type="http", scheme="basic")})

    schemes = security_schemes(("auth", SecurityScheme(type="http", scheme="Basic")), components=configured)

    assert schemes == {"auth": {"type": "http", "scheme": "basic"}}


def test_conflicting_configured_scheme_raises_naming_both_sources() -> None:
    configured = AsyncAPIComponents(security_schemes={"auth": AsyncAPISecurityScheme(type="userPassword")})

    with pytest.raises(
        ImproperlyConfiguredException,
        match=r"securitySchemes/auth.*AsyncAPIConfig\.components.*OpenAPIConfig\.components",
    ):
        security_schemes(("auth", SecurityScheme(type="http", scheme="basic")), components=configured)


def server_app(*servers: Server) -> Litestar:
    @websocket_listener("/events")
    async def events(data: str) -> str:
        return data

    @get("/stream")
    async def stream() -> ServerSentEvent:
        return ServerSentEvent(iter(["tick"]))

    return Litestar(
        route_handlers=[events, stream],
        openapi_config=openapi_config(servers=list(servers)),
        plugins=[ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["news"])],
    )


def test_absolute_openapi_servers_become_websocket_servers_when_enabled() -> None:
    app = server_app(
        Server(url="/"),
        Server(url="https://api.example.com/v1", description="Production"),
        Server(
            url="http://{env}.example.com:{port}",
            variables={"env": ServerVariable(default="dev", enum=["dev", "qa"]), "port": ServerVariable(default="80")},
        ),
    )

    document = AsyncAPIGenerator(app, AsyncAPIConfig(inherit_openapi_servers=True)).build_schema()

    assert document["servers"] == {
        "openapi": {"host": "api.example.com", "protocol": "wss", "pathname": "/v1", "description": "Production"},
        "openapi_2": {
            "host": "{env}.example.com:{port}",
            "protocol": "ws",
            "variables": {"env": {"default": "dev", "enum": ["dev", "qa"]}, "port": {"default": "80"}},
        },
    }
    assert document["channels"]["/events"]["servers"] == [
        {"$ref": "#/servers/openapi"},
        {"$ref": "#/servers/openapi_2"},
    ]
    assert "servers" not in document["channels"]["/stream"]
    assert "servers" not in document["channels"]["news"]


def test_openapi_servers_are_not_inherited_by_default() -> None:
    app = server_app(Server(url="https://api.example.com"))

    document = AsyncAPIGenerator(app, AsyncAPIConfig()).build_schema()
    disabled = AsyncAPIGenerator(
        app, AsyncAPIConfig(inherit_openapi=False, inherit_openapi_servers=True)
    ).build_schema()

    assert document["servers"] == disabled["servers"] == {}
    assert "servers" not in document["channels"]["/events"]


def test_relative_openapi_servers_are_skipped() -> None:
    app = server_app(Server(url="/"), Server(url="/api"), Server(url="ftp://files.example.com"))

    document = AsyncAPIGenerator(app, AsyncAPIConfig(inherit_openapi_servers=True)).build_schema()

    assert document["servers"] == {}
    assert "servers" not in document["channels"]["/events"]


def test_derived_server_name_collision_raises_naming_both_sources() -> None:
    app = server_app(Server(url="https://api.example.com"))
    config = AsyncAPIConfig(
        inherit_openapi_servers=True, servers={"openapi": AsyncAPIServer(host="broker:5672", protocol="amqp")}
    )

    with pytest.raises(
        ImproperlyConfiguredException, match=r"server 'openapi'.*AsyncAPIConfig\.servers.*OpenAPIConfig\.servers"
    ):
        AsyncAPIGenerator(app, config).build_schema()
