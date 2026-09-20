# /// script
# requires-python = ">=3.10"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Configure native renderers explicitly for AsyncAPI paths and media types."""

from typing import cast

from litestar import Litestar
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin, JsonRenderPlugin, YamlRenderPlugin

__all__ = ("app",)

app = Litestar(
    plugins=[
        AsyncAPIPlugin(
            AsyncAPIConfig(
                docs=DocsConfig(
                    path="/events",
                    interactive=True,
                    render_plugins=[
                        AsyncAPIUIRenderPlugin(renderer="scalar"),
                        JsonRenderPlugin(
                            path="/contract.json", media_type=cast("MediaType", "application/vnd.asyncapi+json")
                        ),
                        YamlRenderPlugin(
                            path="/contract.yaml", media_type=cast("MediaType", "application/vnd.asyncapi+yaml")
                        ),
                    ],
                )
            )
        )
    ]
)
