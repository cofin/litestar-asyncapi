from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = (
    "AMQPChannelBinding",
    "AMQPMessageBinding",
    "AMQPServerBinding",
)


@dataclass(slots=True)
class AMQPServerBinding(Binding):
    """AMQP server binding (minimal placeholder model)."""

    virtual_host: str | None = None


@dataclass(slots=True)
class AMQPChannelBinding(Binding):
    """AMQP channel binding (minimal placeholder model)."""

    is_: str | None = field(default=None, metadata={"alias": "is"})
    queue: dict[str, Any] | None = None
    exchange: dict[str, Any] | None = None


@dataclass(slots=True)
class AMQPMessageBinding(Binding):
    """AMQP message binding (minimal placeholder model)."""

    content_encoding: str | None = None
