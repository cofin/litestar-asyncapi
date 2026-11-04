from typing import TYPE_CHECKING

from litestar.channels import ChannelsPlugin
from litestar.exceptions import ImproperlyConfiguredException
from litestar.routes.websocket import WebSocketRoute

from litestar_asyncapi._compat import (
    ChannelsPluginTopics,
    channels_plugin_topics,
    generated_channels_mode,
    generated_channels_plugin,
)
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

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator

__all__ = ("extract_channels_plugin_channels",)

TOPIC_DESCRIPTION = "ChannelsPlugin broker topic"


def extract_channels_plugin_channels(
    app: "Litestar", *, schema_generator: "AsyncAPISchemaGenerator", config: "AsyncAPIConfig | None" = None
) -> list[DiscoveredChannel]:
    """Describe ChannelsPlugin generated sockets and configured topics as send-only channels.

    Generated routes keep their path as channel key. Configured topics without a generated fixed-topic
    route become topic-only channels keyed by the topic name. Topics come from the snapshot the
    application's ``AsyncAPIPlugin`` takes at init, or are read directly without one.

    Args:
        app: Litestar application.
        schema_generator: Schema generator shared with the document build.
        config: Optional AsyncAPI configuration controlling which channels are included.

    Returns:
        A list of discovered channels.

    Raises:
        ImproperlyConfiguredException: If two ChannelsPlugin instances configure the same topic.
    """
    from litestar_asyncapi import AsyncAPIConfig

    config = config or AsyncAPIConfig()
    configured = _configured_topics(app)
    if not config.include_channels_plugin:
        return []
    owners: dict[str, int] = {}
    for index, (_, snapshot) in enumerate(configured):
        for topic in snapshot.topics:
            if topic in owners:
                message = f"ChannelsPlugin topic {topic!r} is configured on both ChannelsPlugin[{owners[topic]}] and ChannelsPlugin[{index}]"
                raise ImproperlyConfiguredException(message)
            owners[topic] = index

    discovered: list[DiscoveredChannel] = []
    routed: set[tuple[int, str]] = set()
    for route in app.routes:
        if not isinstance(route, WebSocketRoute):
            continue
        plugin = generated_channels_plugin(route.route_handler, app)
        if plugin is None:
            continue
        index, snapshot = next((i, item[1]) for i, item in enumerate(configured) if item[0] is plugin)
        if not snapshot.arbitrary_channels_allowed:
            routed.add((index, route.path_format.removeprefix(snapshot.root_path)))
        if not _should_include_handler(route.route_handler):
            continue
        mode = generated_channels_mode(route.route_handler, app)
        provenance = f"ChannelsPlugin route {route.path_format} handler {route.route_handler.handler_name}"
        discovered.append(
            DiscoveredChannel(
                route_identity=route,
                key=route.path_format,
                address=route.path_format,
                source=DiscoverySource.CHANNELS_PLUGIN,
                provenance=provenance,
                parameters=_path_parameters_to_parameters(route.path_parameters) or None,
                bindings={},
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

    if config.include_channels_plugin_topics:
        discovered.extend(
            _topic_channel(topic, provenance=f"ChannelsPlugin[{index}] topic {topic!r}")
            for index, (_, snapshot) in enumerate(configured)
            for topic in snapshot.topics
            if (index, topic) not in routed
        )
    return discovered


def _configured_topics(app: "Litestar") -> list[tuple[ChannelsPlugin, ChannelsPluginTopics]]:
    """Pair every application ChannelsPlugin with its init-time topic snapshot, in plugin order.

    Returns:
        The plugins and their configured topics.
    """
    from litestar_asyncapi.plugins.core import AsyncAPIPlugin

    owner = next((plugin for plugin in app.plugins if isinstance(plugin, AsyncAPIPlugin)), None)
    snapshots = owner._channels_topics if owner is not None else ()
    configured = []
    for plugin in app.plugins:
        if isinstance(plugin, ChannelsPlugin):
            snapshot = next((item for source, item in snapshots if source is plugin), None)
            configured.append((plugin, snapshot or channels_plugin_topics(plugin)))
    return configured


def _topic_channel(topic: str, *, provenance: str) -> DiscoveredChannel:
    """Describe a configured topic without a generated route as a broker channel keyed by its name.

    Returns:
        A topic-only channel with one ``send`` operation.
    """
    return DiscoveredChannel(
        route_identity=None,
        key=topic,
        address=topic,
        description=TOPIC_DESCRIPTION,
        source=DiscoverySource.CHANNELS_PLUGIN,
        provenance=provenance,
        bindings={},
        operations=[
            DiscoveredOperation(
                action=OperationAction.SEND, provenance=provenance, messages=[MessageDefinition(payload=Schema())]
            )
        ],
    )
