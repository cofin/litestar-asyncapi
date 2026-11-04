from dataclasses import dataclass
from typing import Any, Literal

from litestar import Litestar, WebSocket, websocket_listener
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, Contact, License, OAuthFlow, OAuthFlows, SecurityScheme
from litestar.security.jwt import JWTAuth

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig

__all__ = ("app_3_0", "app_3_1")


@dataclass
class Ping:
    sequence: int


@websocket_listener("/ping")
async def ping(data: Ping) -> Ping:
    return data


def retrieve_user(token: Any, connection: WebSocket) -> None:
    return None


def create_app(spec_version: Literal["3.0.0", "3.1.0"]) -> Litestar:
    auth = JWTAuth[Any](retrieve_user_handler=retrieve_user, token_secret="fixture-secret-with-32-characters")
    schemes = {
        "basic": SecurityScheme(type="http", scheme="Basic"),
        "headerKey": SecurityScheme(type="apiKey", name="X-API-Key", security_scheme_in="header"),
        "queryKey": SecurityScheme(type="apiKey", name="api_key", security_scheme_in="query"),
        "cookieKey": SecurityScheme(type="apiKey", name="session", security_scheme_in="cookie"),
        "oauth": SecurityScheme(
            type="oauth2",
            flows=OAuthFlows(
                implicit=OAuthFlow(authorization_url="https://id.example.com/authorize"),
                password=OAuthFlow(token_url="https://id.example.com/token"),
                client_credentials=OAuthFlow(
                    token_url="https://id.example.com/token", scopes={"events:read": "Read events"}
                ),
                authorization_code=OAuthFlow(
                    authorization_url="https://id.example.com/authorize",
                    token_url="https://id.example.com/token",
                    refresh_url="https://id.example.com/refresh",
                ),
            ),
        ),
        "openId": SecurityScheme(
            type="openIdConnect", open_id_connect_url="https://id.example.com/.well-known/openid-configuration"
        ),
        "mtls": SecurityScheme(type="mutualTLS", description="Client certificate"),
    }
    openapi_config = OpenAPIConfig(
        title="OpenAPI inheritance fixture",
        version="2.0.0",
        description="Metadata and security schemes inherited from OpenAPIConfig.",
        contact=Contact(name="Realtime team", email="realtime@example.com"),
        license=License(name="MIT", identifier="MIT"),
        terms_of_service="https://example.com/terms",
        components=Components(security_schemes=schemes),
    )
    config = AsyncAPIConfig(spec_version=spec_version, docs=DocsConfig(enabled=False))
    return Litestar(
        route_handlers=[ping],
        openapi_config=openapi_config,
        on_app_init=[auth.on_app_init],
        plugins=[AsyncAPIPlugin(config)],
    )


app_3_0 = create_app("3.0.0")
app_3_1 = create_app("3.1.0")
