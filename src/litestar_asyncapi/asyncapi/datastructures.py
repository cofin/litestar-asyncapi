from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from litestar_asyncapi.spec import (
    CorrelationId,
    MessageTrait,
    OperationAction,
    OperationTrait,
    Parameter,
    Reference,
    Reply,
    SecurityScheme,
    Tag,
)

__all__ = (
    "SOURCE_EXTENSION",
    "SOURCE_MARKERS",
    "ChannelDefinition",
    "DiscoveredChannel",
    "DiscoveredOperation",
    "DiscoverySource",
    "MessageDefinition",
    "OperationDefinition",
)


class DiscoverySource(StrEnum):
    """Identify the source of a discovered channel."""

    WEBSOCKET = "websocket"
    CHANNELS_PLUGIN = "channels-plugin"
    CONFIG = "config"
    SSE = "sse"


SOURCE_EXTENSION = "x-litestar-source"
"""Channel extension naming the transport of a discovered channel."""

SOURCE_MARKERS: dict[DiscoverySource, str] = {
    DiscoverySource.WEBSOCKET: "websocket",
    DiscoverySource.CHANNELS_PLUGIN: "channels",
    DiscoverySource.SSE: "sse",
}
"""``x-litestar-source`` values for discovered channels; explicit config channels carry none."""


@dataclass(slots=True)
class MessageDefinition:
    """A message contract retaining Python payload and header types until assembly."""

    payload: object | None = None
    """Payload type, converted to a JSON Schema when the document is built.

    A spec ``Schema``, ``Reference``, ``MultiFormatSchema``, schema dict or bool is used as given.
    """
    name: str | None = None
    """Machine-friendly message name."""
    title: str | None = None
    """Human-friendly message title."""
    summary: str | None = None
    """Short summary of the message."""
    description: str | None = None
    """Longer description of the message; CommonMark is allowed."""
    examples: list[object] | None = None
    """Example payloads; an empty list suppresses generated examples."""
    headers: object | None = None
    """Header type or schema, converted like ``payload``."""
    correlation_id: CorrelationId | Reference | None = None
    """Location of the correlation id in the message."""
    content_type: str | None = None
    """Media type of the payload; inferred from the payload schema when omitted."""
    traits: list[str | MessageTrait | Reference] | None = None
    """Message traits, given by name of a configured trait, as an object or as a reference."""
    bindings: dict[str, Any] | Reference | None = None
    """Protocol-specific message bindings."""
    tags: list[Tag | Reference] | None = None
    """Tags for logical grouping."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(slots=True)
class OperationDefinition:
    """An application-perspective operation and its named message choices."""

    action: OperationAction | str
    """Direction from the application's perspective: ``send`` or ``receive``."""
    messages: list[MessageDefinition] | None = None
    """Messages the operation carries; ``None`` keeps the inferred messages."""
    operation_id: str | None = None
    """Key of the operation in the document; derived from the channel key when omitted."""
    title: str | None = None
    """Human-friendly operation title."""
    summary: str | None = None
    """Short summary of the operation."""
    description: str | None = None
    """Longer description of the operation; CommonMark is allowed."""
    traits: list[str | OperationTrait | Reference] | None = None
    """Operation traits, given by name of a configured trait, as an object or as a reference."""
    tags: list[Tag | Reference] | None = None
    """Tags for logical grouping."""
    security: list[SecurityScheme | Reference] | None = None
    """Security schemes that apply to the operation."""
    bindings: dict[str, Any] | Reference | None = None
    """Protocol-specific operation bindings."""
    reply: Reply | Reference | None = None
    """Reply that the operation expects, for request and reply patterns."""

    def __post_init__(self) -> None:
        action = self.action.strip().lower()
        if action not in {item.value for item in OperationAction}:
            detail = f"Invalid action {self.action!r}. Expected 'send' or 'receive'."
            raise ValueError(detail)
        self.action = OperationAction(action)
        names: set[str | None] = set()
        for message in self.messages or []:
            if message.name in names:
                detail = f"Conflicting message declarations for {message.name!r} in operation {self.operation_id or self.action.value!r}"
                raise ValueError(detail)
            names.add(message.name)


@dataclass(slots=True)
class ChannelDefinition:
    """An explicit channel keyed independently from its transport address."""

    key: str
    """Key of the channel in the document's ``channels`` map."""
    address: str
    """Transport address of the channel, such as a WebSocket path or broker topic."""
    operations: Sequence[OperationDefinition] = ()
    """Operations on the channel."""
    parameters: dict[str, Parameter | Reference] | None = None
    """Parameters for expressions in ``address``."""
    servers: list[Reference] | None = None
    """References to the servers that host the channel; all servers when omitted."""
    bindings: dict[str, Any] | Reference | None = None
    """Protocol-specific channel bindings."""
    description: str | None = None
    """Description of the channel; CommonMark is allowed."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""


@dataclass(kw_only=True)
class DiscoveredOperation(OperationDefinition):
    """An operation definition with its source route and handler description."""

    __slots__ = ("provenance",)

    provenance: str
    """Route and handler that produced the operation, quoted in conflict errors."""


@dataclass(kw_only=True)
class DiscoveredChannel(ChannelDefinition):
    """A channel definition with discovery provenance."""

    __slots__ = ("provenance", "route_identity", "source")

    source: DiscoverySource
    """Discovery source, which selects the channel's ``x-litestar-source`` marker."""
    provenance: str
    """Route, topic or configuration that produced the channel, quoted in conflict errors."""
    route_identity: object | None
    """Route that produced the channel, or ``None`` for topic-only and configured channels."""
