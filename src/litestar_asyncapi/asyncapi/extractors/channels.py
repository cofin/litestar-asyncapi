from typing import TYPE_CHECKING

from litestar.routes.websocket import WebSocketRoute

from litestar_asyncapi._compat import generated_channels_mode
from litestar_asyncapi.asyncapi.datastructures import (
    DiscoveredChannel,
    DiscoveredOperation,
    DiscoverySource,
    MessageDefinition,
)
from litestar_asyncapi.asyncapi.extractors.websocket import _path_parameters_to_parameters, _should_include_handler
from litestar_asyncapi.spec import OperationAction, Schema

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

__all__ = ("extract_channels_plugin_channels",)


def extract_channels_plugin_channels(
    app: "Litestar", *, schema_generator: "AsyncAPISchemaGenerator"
) -> list[DiscoveredChannel]:
    """Describe finalized native Channels sockets without exposing broker subscriptions."""
    discovered = []
    for route in app.routes:
        if not isinstance(route, WebSocketRoute) or not _should_include_handler(route.route_handler):
            continue
        mode = generated_channels_mode(route.route_handler, app)
        if mode is None:
            continue
        provenance = f"ChannelsPlugin route {route.path_format} handler {route.route_handler.handler_name}"
        discovered.append(
            DiscoveredChannel(
                key=route.path_format,
                address=route.path_format,
                source=DiscoverySource.CHANNELS_PLUGIN,
                provenance=provenance,
                parameters=_path_parameters_to_parameters(route.path_parameters, schema_generator=schema_generator)
                or None,
                operations=[
                    DiscoveredOperation(
                        action=OperationAction.SEND,
                        provenance=provenance,
                        messages=[
                            MessageDefinition(
                                payload=Schema(),
                                content_type="text/plain" if mode == "text" else "application/octet-stream",
                                extensions={"x-websocket-mode": mode},
                            )
                        ],
                    )
                ],
            )
        )
    return discovered
