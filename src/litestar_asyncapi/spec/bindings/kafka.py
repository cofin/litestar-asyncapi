from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = ("KafkaChannelBinding", "KafkaMessageBinding", "KafkaServerBinding")


@dataclass(slots=True)
class KafkaServerBinding(Binding):
    """Kafka server binding (minimal placeholder model)."""

    schema_registry_url: str | None = None
    schema_registry_vendor: str | None = None


@dataclass(slots=True)
class KafkaChannelBinding(Binding):
    """Kafka channel binding (minimal placeholder model)."""

    topic: str | None = None
    partitions: int | None = None
    replicas: int | None = None
    topic_configuration: dict[str, Any] | None = None


@dataclass(slots=True)
class KafkaMessageBinding(Binding):
    """Kafka message binding (minimal placeholder model)."""

    key: dict[str, Any] | bool | None = None
    schema_id_location: str | None = None
    schema_id_payload_encoding: str | None = None
    schema_lookup_strategy: str | None = None
