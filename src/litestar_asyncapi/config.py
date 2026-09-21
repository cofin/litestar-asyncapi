from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

from litestar.utils.path import normalize_path

from litestar_asyncapi.asyncapi.datastructures import ChannelDefinition
from litestar_asyncapi.spec import Components, MessageTrait, OperationTrait, Reference, Server

if TYPE_CHECKING:
    from litestar.enums import MediaType
    from litestar.types import Dependencies, Guard

    from litestar_asyncapi.plugins import AsyncAPIRenderPlugin

__all__ = ("AsyncAPIConfig", "DocsConfig")


def _default_render_plugins(
    renderer: Literal["asyncapi", "scalar"] = "asyncapi", interactive: bool = False
) -> list["AsyncAPIRenderPlugin"]:
    from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin, JsonRenderPlugin

    return [
        AsyncAPIUIRenderPlugin(renderer=renderer, interactive=interactive and renderer == "asyncapi"),
        JsonRenderPlugin(path="/asyncapi.json", media_type=cast("MediaType", "application/vnd.asyncapi+json")),
    ]


def _validate_create_examples(value: object) -> None:
    if not isinstance(value, bool):
        message = "create_examples must be a bool; provide explicit message examples instead of custom factories"
        raise TypeError(message)


@dataclass(slots=True)
class DocsConfig:
    """Documentation routes and optional interactive UI settings."""

    path: str = "/asyncapi"
    enabled: bool = True
    guards: Sequence["Guard"] = ()
    dependencies: "Dependencies | None" = None
    renderer: Literal["asyncapi", "scalar"] = "asyncapi"
    interactive: bool = False
    yaml: bool = False
    render_plugins: list["AsyncAPIRenderPlugin"] | None = None

    def __post_init__(self) -> None:
        from litestar_asyncapi.docs import renderer_name
        from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin, JsonRenderPlugin, YamlRenderPlugin

        plugins = (
            list(self.render_plugins)
            if self.render_plugins is not None
            else _default_render_plugins(self.renderer, self.interactive)
        )
        if not any(isinstance(plugin, JsonRenderPlugin) for plugin in plugins):
            plugins.append(
                JsonRenderPlugin(path="/asyncapi.json", media_type=cast("MediaType", "application/vnd.asyncapi+json"))
            )
        if self.yaml and not any(isinstance(plugin, YamlRenderPlugin) for plugin in plugins):
            plugins.append(
                YamlRenderPlugin(
                    path=("/asyncapi.yaml", "/asyncapi.yml"),
                    media_type=cast("MediaType", "application/vnd.asyncapi+yaml"),
                )
            )
        if self.interactive and not any(
            isinstance(plugin, AsyncAPIUIRenderPlugin) and plugin.role == "playground" for plugin in plugins
        ):
            plugins.append(AsyncAPIUIRenderPlugin(path="/playground", interactive=True, role="playground"))
        paths: set[str] = set()
        names: set[str] = set()
        for plugin in plugins:
            name = renderer_name(plugin)
            if name in names:
                message = f"Duplicate documentation renderer name: {name}"
                raise ValueError(message)
            names.add(name)
            for path in plugin.paths:
                normalized = normalize_path(path)
                if normalized in paths or normalized == "/assets" or normalized.startswith("/assets/"):
                    message = f"Duplicate documentation route path: {normalized}"
                    raise ValueError(message)
                paths.add(normalized)
        self.render_plugins = plugins


@dataclass(slots=True)
class AsyncAPIConfig:
    """Configuration for the AsyncAPI plugin.

    This configuration class defines the settings for generating AsyncAPI
    documentation for event-driven APIs.
    """

    title: str = "AsyncAPI"
    """The title of the AsyncAPI document."""
    version: str = "1.0.0"
    """The version of the API."""
    description: str | None = None
    """An optional description of the API."""
    default_content_type: str | None = None
    """Default content type for messages, if not otherwise specified."""
    use_handler_docstrings: bool = False
    """Whether to use handler docstrings for operation descriptions."""
    create_examples: bool = False
    """Whether to auto-generate examples for message payloads."""

    strict_uniqueness: bool = False
    """Whether to raise an exception on operationId collision instead of suffixing."""

    include_websocket_routes: bool = True
    """Whether to include websocket routes discovered from the application."""

    include_raw_websocket_routes: bool = False
    """Include uncertain raw socket contracts with a warning when no explicit metadata exists."""

    include_channels_plugin: bool = True
    """Whether to include ChannelsPlugin channels (best-effort)."""

    servers: dict[str, Server | Reference | dict[str, Any]] = field(default_factory=dict)
    """Server definitions for the AsyncAPI document."""

    use_cache: bool = True
    """Whether plugin methods should cache built documents for subsequent calls."""

    components: Components = field(default_factory=Components)

    spec_version: Literal["3.0.0", "3.1.0"] = "3.1.0"
    channels: list[ChannelDefinition] = field(default_factory=list)
    docs: "DocsConfig" = field(default_factory=DocsConfig)

    operation_traits: dict[str, OperationTrait | Reference | dict[str, Any]] = field(default_factory=dict)
    """Reusable operation traits registered under `components.operationTraits`."""

    message_traits: dict[str, MessageTrait | Reference | dict[str, Any]] = field(default_factory=dict)
    """Reusable message traits registered under `components.messageTraits`."""

    def __post_init__(self) -> None:
        _validate_create_examples(self.create_examples)

    def to_servers(self) -> dict[str, Server | Reference]:
        """Return a mapping of server definitions.

        Returns:
            A mapping of server name to :class:`~litestar_asyncapi.spec.Server`.
        """
        servers: dict[str, Server | Reference] = {}
        for name, value in self.servers.items():
            if isinstance(value, (Server, Reference)):
                servers[name] = value
            else:
                servers[name] = Server(**value)
        return servers

    def to_operation_traits(self) -> dict[str, OperationTrait | Reference]:
        """Return a mapping of operation trait definitions.

        Returns:
            A mapping of trait name to :class:`~litestar_asyncapi.spec.OperationTrait`.
        """
        traits: dict[str, OperationTrait | Reference] = {}
        for name, value in self.operation_traits.items():
            if isinstance(value, (OperationTrait, Reference)):
                traits[name] = value
            else:
                traits[name] = OperationTrait(**value)
        return traits

    def to_message_traits(self) -> dict[str, MessageTrait | Reference]:
        """Return a mapping of message trait definitions.

        Returns:
            A mapping of trait name to :class:`~litestar_asyncapi.spec.MessageTrait`.
        """
        traits: dict[str, MessageTrait | Reference] = {}
        for name, value in self.message_traits.items():
            if isinstance(value, (MessageTrait, Reference)):
                traits[name] = value
            else:
                traits[name] = MessageTrait(**value)
        return traits
