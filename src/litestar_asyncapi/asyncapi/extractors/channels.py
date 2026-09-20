from typing import TYPE_CHECKING, cast

from litestar.channels.plugin import ChannelsPlugin

from litestar_asyncapi.asyncapi.datastructures import (
    DiscoveredChannel,
    DiscoveredMessage,
    DiscoveredOperation,
    DiscoverySource,
)
from litestar_asyncapi.spec import OperationAction, Parameter, Schema, SchemaType

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


__all__ = ("extract_channels_plugin_channels",)


def extract_channels_plugin_channels(
    app: "Litestar", *, schema_generator: "AsyncAPISchemaGenerator"
) -> list[DiscoveredChannel]:
    """Extract channels from Litestar's ChannelsPlugin (best-effort).

    Notes:
        - If ChannelsPlugin is configured with ``create_ws_route_handlers=True``, websocket extraction will already
          discover the generated websocket routes, so this extractor returns an empty list to avoid duplication.
        - ChannelsPlugin does not currently expose a stable public list of declared channels; this uses its internal
          ``_channels`` mapping when present.

    Args:
        app: Litestar application.
        schema_generator: Schema generator used to produce placeholder schemas.

    Returns:
        A list of discovered channels.
    """
    plugin = next((p for p in app.plugins if isinstance(p, ChannelsPlugin)), None)
    if plugin is None:
        return []

    if plugin._create_route_handlers:
        return []

    root_path = plugin._handler_root_path

    placeholder_payload = Schema(type=SchemaType.OBJECT)
    send_operation = DiscoveredOperation(
        action=OperationAction.SEND,
        operation_id=None,
        message=DiscoveredMessage(payload=placeholder_payload, content_type="application/json"),
    )

    discovered: list[DiscoveredChannel] = []
    if plugin._arbitrary_channels_allowed:
        channel_name_param = Parameter(description="The name of the arbitrary channel.")
        discovered.append(
            DiscoveredChannel(
                address=f"{root_path}{{channel_name}}",
                source=DiscoverySource.CHANNELS_PLUGIN,
                parameters={"channel_name": channel_name_param},
                operations=[send_operation],
            )
        )
        return discovered

    channel_map = cast("dict[str, object]", plugin._channels)
    discovered.extend(
        DiscoveredChannel(
            address=f"{root_path}{name}",
            source=DiscoverySource.CHANNELS_PLUGIN,
            parameters=None,
            operations=[send_operation],
        )
        for name in channel_map
    )

    return discovered
