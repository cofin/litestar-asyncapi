"""Serve generated documents from the installed package for real-browser tests."""

import os
from dataclasses import dataclass
from typing import Literal

import uvicorn
from litestar import Litestar, asgi
from litestar.types import Receive, Scope, Send

from litestar_asyncapi import (
    AsyncAPIConfig,
    AsyncAPIPlugin,
    ChannelDefinition,
    DocsConfig,
    MessageDefinition,
    OperationDefinition,
)
from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin, JsonRenderPlugin
from litestar_asyncapi.spec import MultiFormatSchema, Server

__all__ = ("Node", "config", "create_app")


@dataclass(slots=True)
class Node:
    value: str
    children: list["Node"]


def config(renderer: Literal["asyncapi", "scalar"], version: Literal["3.0.0", "3.1.0"], path: str) -> AsyncAPIConfig:
    payload = {
        "type": "object",
        "properties": {
            "pair": {
                "type": "array",
                "items": [
                    {"type": "string", "description": "POSITION_ONE_STRING"},
                    {"type": "integer", "description": "POSITION_TWO_INTEGER"},
                ],
                "additionalItems": False,
                "minItems": 2,
                "maxItems": 2,
            },
            "empty": {"type": "array", "maxItems": 0},
            "literal": {"type": "null", "const": None, "default": None},
        },
    }
    return AsyncAPIConfig(
        title="Packaged UI <script>window.pwned=1</script>",
        spec_version=version,
        servers={"socket": Server(host="example.invalid", protocol="wss")},
        channels=[
            ChannelDefinition(
                key="events",
                address="/events",
                operations=[
                    OperationDefinition(
                        action="receive",
                        messages=[
                            MessageDefinition(
                                name="TupleMessage",
                                payload=payload,
                                headers={"type": "object", "properties": {"requestId": {"type": "string"}}},
                            ),
                            MessageDefinition(
                                name="ForbiddenMessage",
                                payload=MultiFormatSchema("application/schema+json;version=draft-07", False),
                            ),
                            MessageDefinition(name="RecursiveMessage", payload=Node),
                        ],
                    )
                ],
            )
        ],
        docs=DocsConfig(path=path, renderer=renderer, enabled=False),
    )


def create_app() -> Litestar:
    routes = []
    for renderer in ("asyncapi", "scalar", "mounted/docs"):
        for version in ("3.1.0",) if renderer == "mounted/docs" else ("3.0.0", "3.1.0"):
            path = f"/{renderer}" if version == "3.1.0" else f"/v30/{renderer}"
            selected = config("asyncapi" if renderer == "mounted/docs" else renderer, version, "/")
            if renderer == "mounted/docs":
                selected.docs = DocsConfig(
                    path="/",
                    enabled=False,
                    render_plugins=[AsyncAPIUIRenderPlugin(), JsonRenderPlugin(path="/contract.json")],
                )
            plugin = AsyncAPIPlugin(selected)
            inner = Litestar([plugin.create_docs_router()])

            def mount(application: Litestar, prefix: str) -> asgi:
                @asgi(prefix, is_mount=True, copy_scope=True)
                async def handler(scope: Scope, receive: Receive, send: Send) -> None:
                    scope["root_path"] = scope.get("root_path", "") + prefix
                    scope["path"] = scope["root_path"] + scope["path"]
                    await application(scope, receive, send)

                return handler

            routes.append(mount(inner, path))
    return Litestar(routes)


if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=int(os.environ.get("PORT", "8917")))
