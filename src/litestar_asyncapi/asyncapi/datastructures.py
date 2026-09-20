from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec import CorrelationId, Message, OperationAction, Parameter, Reference, Schema

__all__ = ("DiscoveredChannel", "DiscoveredMessage", "DiscoveredOperation", "DiscoverySource")

if TYPE_CHECKING:
    from collections.abc import Sequence


class DiscoverySource(str, Enum):
    """Identify the source of a discovered channel."""

    WEBSOCKET = "websocket"
    CHANNELS_PLUGIN = "channels-plugin"


@dataclass(slots=True)
class DiscoveredMessage:
    """Internal representation of a discovered message."""

    payload: Schema | Reference | dict[str, Any] | bool | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    examples: list[Any] | None = None
    headers: Schema | Reference | dict[str, Any] | bool | None = None
    correlation_id: CorrelationId | Reference | None = None
    content_type: str | None = None
    traits: list[str] | None = None

    def to_spec_message(self) -> Message:
        """Create an AsyncAPI Message object.

        Returns:
            A :class:`~litestar_asyncapi.spec.Message` instance.
        """

        return Message(
            name=self.name,
            title=self.title,
            summary=self.summary,
            description=self.description,
            examples=self.examples,
            headers=self.headers,
            payload=self.payload,
            correlation_id=self.correlation_id,
            content_type=self.content_type,
        )


@dataclass(slots=True)
class DiscoveredOperation:
    """Internal representation of a discovered operation."""

    action: OperationAction
    message: DiscoveredMessage | None = None
    operation_id: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    traits: list[str] | None = None


@dataclass(slots=True)
class DiscoveredChannel:
    """Internal representation of a discovered AsyncAPI channel."""

    address: str
    source: DiscoverySource
    parameters: dict[str, Parameter] | None = None
    operations: "Sequence[DiscoveredOperation]" = ()
