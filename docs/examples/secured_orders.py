# /// script
# requires-python = ">=3.11"
# dependencies = ["litestar[standard,jwt]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""A JWT-protected WebSocket whose security scheme and server come from the OpenAPI config."""

from dataclasses import dataclass
from typing import Any

from litestar import Litestar, websocket_listener
from litestar.connection import ASGIConnection
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Server
from litestar.security.jwt import JWTAuth, Token

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, asyncapi_message, asyncapi_operation
from litestar_asyncapi.spec import CorrelationId, OperationTrait, Tag

__all__ = ("app",)


@dataclass
class User:
    name: str


@dataclass
class PlaceOrder:
    order_id: str
    sku: str
    quantity: int


@dataclass
class OrderStatus:
    order_id: str
    status: str


async def retrieve_user(token: Token, connection: ASGIConnection[Any, Any, Any, Any]) -> User:
    return User(name=token.sub)


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user,
    token_secret="development-secret-replace-in-production",
    exclude=["/asyncapi", "/schema"],
)
by_order_id = CorrelationId(location="$message.payload#/order_id")


@asyncapi_operation(action="receive", security=["BearerToken"], traits=["orders"])
@asyncapi_operation(action="send", security=["BearerToken"], traits=["orders"])
@asyncapi_message(action="receive", name="PlaceOrder", payload=PlaceOrder, correlation_id=by_order_id)
@asyncapi_message(action="send", name="OrderStatus", payload=OrderStatus, correlation_id=by_order_id)
@websocket_listener("/orders")
async def orders(data: PlaceOrder) -> OrderStatus:
    return OrderStatus(order_id=data.order_id, status="accepted")


app = Litestar(
    route_handlers=[orders],
    on_app_init=[jwt_auth.on_app_init],
    openapi_config=OpenAPIConfig(
        title="Orders", version="1.0.0", servers=[Server(url="https://orders.example.com", description="Production")]
    ),
    plugins=[
        AsyncAPIPlugin(
            AsyncAPIConfig(
                inherit_openapi_servers=True, operation_traits={"orders": OperationTrait(tags=[Tag(name="orders")])}
            )
        )
    ],
)
