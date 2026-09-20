from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
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
    "ChannelDefinition",
    "DiscoveredChannel",
    "DiscoveredOperation",
    "DiscoverySource",
    "MessageDefinition",
    "OperationDefinition",
)


class DiscoverySource(str, Enum):
    """Identify the source of a discovered channel."""

    WEBSOCKET = "websocket"
    CHANNELS_PLUGIN = "channels-plugin"
    CONFIG = "config"


@dataclass(slots=True)
class MessageDefinition:
    """A message contract retaining Python payload and header types until assembly."""

    payload: object | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    examples: list[object] | None = None
    headers: object | None = None
    correlation_id: CorrelationId | Reference | None = None
    content_type: str | None = None
    traits: list[str | MessageTrait | Reference] | None = None
    bindings: dict[str, Any] | Reference | None = None
    tags: list[Tag | Reference] | None = None
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OperationDefinition:
    """An application-perspective operation and its named message choices."""

    action: OperationAction | str
    messages: list[MessageDefinition] | None = None
    operation_id: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    traits: list[str | OperationTrait | Reference] | None = None
    tags: list[Tag | Reference] | None = None
    security: list[SecurityScheme | Reference] | None = None
    bindings: dict[str, Any] | Reference | None = None
    reply: Reply | Reference | None = None

    def __post_init__(self) -> None:
        self.action = OperationAction(self.action)
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
    address: str
    operations: Sequence[OperationDefinition] = ()
    parameters: dict[str, Parameter | Reference] | None = None
    servers: list[Reference] | None = None
    bindings: dict[str, Any] | Reference | None = None


@dataclass(kw_only=True)
class DiscoveredOperation(OperationDefinition):
    """An operation definition with its source route and handler description."""

    __slots__ = ("provenance",)

    provenance: str


@dataclass(kw_only=True)
class DiscoveredChannel(ChannelDefinition):
    """A channel definition with discovery provenance."""

    __slots__ = ("provenance", "source")

    source: DiscoverySource
    provenance: str
