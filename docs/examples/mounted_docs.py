# /// script
# requires-python = ">=3.10"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Mount guarded documentation with native Litestar routing."""

from litestar import Litestar, Router
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig

__all__ = ("app", "docs_guard")


def docs_guard(connection: ASGIConnection, handler: BaseRouteHandler) -> None:
    if connection.headers.get("authorization") != "demo-token":
        raise NotAuthorizedException


plugin = AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(enabled=False, guards=[docs_guard])))
app = Litestar([Router("/service", route_handlers=[plugin.create_docs_router()])], plugins=[plugin])
