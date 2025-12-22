from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = (
    "KafkaChannelBinding",
    "KafkaMessageBinding",
    "KafkaServerBinding",
)


@dataclass(slots=True)
class KafkaServerBinding(Binding):
    """Kafka server binding (minimal placeholder model)."""

    client_id: str | None = None


@dataclass(slots=True)
class KafkaChannelBinding(Binding):
    """Kafka channel binding (minimal placeholder model)."""

    topic: str | None = None
    partitions: int | None = None


@dataclass(slots=True)
class KafkaMessageBinding(Binding):
    """Kafka message binding (minimal placeholder model)."""

    key: dict[str, Any] | None = None
