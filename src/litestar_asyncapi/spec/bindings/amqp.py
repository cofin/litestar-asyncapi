from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = ("AMQPChannelBinding", "AMQPMessageBinding", "AMQPServerBinding")


@dataclass(slots=True)
class AMQPServerBinding(Binding):
    """AMQP server binding, which defines no protocol-specific fields."""


@dataclass(slots=True)
class AMQPChannelBinding(Binding):
    """AMQP channel binding describing the queue or exchange behind a channel."""

    is_: str | None = field(default=None, metadata={"alias": "is"})
    """Channel type, serialized as ``is``: ``queue`` or ``routingKey``."""
    queue: dict[str, Any] | None = None
    """Queue properties when the channel is a queue."""
    exchange: dict[str, Any] | None = None
    """Exchange properties when the channel is a routing key."""


@dataclass(slots=True)
class AMQPMessageBinding(Binding):
    """AMQP message binding."""

    content_encoding: str | None = None
    """MIME encoding of the message content."""
    message_type: str | None = None
    """Application-specific message type."""
