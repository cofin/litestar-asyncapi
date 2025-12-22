from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec import MessageTrait, OperationTrait, Reference, Server

if TYPE_CHECKING:
    from litestar_asyncapi.plugins import AsyncAPIRenderPlugin


def _default_render_plugins() -> list["AsyncAPIRenderPlugin"]:
    from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin, JsonRenderPlugin, YamlRenderPlugin

    return [AsyncAPIUIRenderPlugin(), JsonRenderPlugin(), YamlRenderPlugin()]


@dataclass
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
    default_content_type: str = "application/json"
    """Default content type for messages, if not otherwise specified."""
    use_handler_docstrings: bool = False
    """Whether to use handler docstrings for operation descriptions."""
    create_examples: bool | object | dict[type[Any], object] = False
    """Whether to auto-generate examples for message payloads."""
    random_seed: int | None = None
    """Optional random seed for deterministic example generation."""

    include_websocket_routes: bool = True
    """Whether to include websocket routes discovered from the application."""

    include_channels_plugin: bool = True
    """Whether to include ChannelsPlugin channels (best-effort)."""

    servers: dict[str, Server | dict[str, Any]] = field(default_factory=dict)
    """Server definitions for the AsyncAPI document."""

    use_cache: bool = True
    """Whether plugin methods should cache built documents for subsequent calls."""

    path: str = "/asyncapi"
    """Base path for the docs router."""

    render_plugins: list["AsyncAPIRenderPlugin"] = field(default_factory=_default_render_plugins)
    """Render plugins used to serve JSON/YAML/UI endpoints."""

    enable_routes: bool = True
    """Whether to register the docs router during app initialization."""

    operation_traits: dict[str, OperationTrait | dict[str, Any]] = field(default_factory=dict)
    """Reusable operation traits registered under `components.operationTraits`."""

    message_traits: dict[str, MessageTrait | dict[str, Any]] = field(default_factory=dict)
    """Reusable message traits registered under `components.messageTraits`."""

    def to_servers(self) -> dict[str, Server]:
        """Return a mapping of server definitions.

        Returns:
            A mapping of server name to :class:`~litestar_asyncapi.spec.Server`.
        """
        servers: dict[str, Server] = {}
        for name, value in self.servers.items():
            if isinstance(value, Server):
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
            if isinstance(value, OperationTrait):
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
            if isinstance(value, MessageTrait):
                traits[name] = value
            else:
                traits[name] = MessageTrait(**value)
        return traits
