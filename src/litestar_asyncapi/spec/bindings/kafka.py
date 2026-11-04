from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.bindings.base import Binding

__all__ = ("KafkaChannelBinding", "KafkaMessageBinding", "KafkaServerBinding")


@dataclass(slots=True)
class KafkaServerBinding(Binding):
    """Kafka server binding naming the schema registry."""

    schema_registry_url: str | None = None
    """URL of the schema registry."""
    schema_registry_vendor: str | None = None
    """Vendor of the schema registry, such as ``confluent``."""


@dataclass(slots=True)
class KafkaChannelBinding(Binding):
    """Kafka channel binding describing the topic."""

    topic: str | None = None
    """Kafka topic name, when it differs from the channel address."""
    partitions: int | None = None
    """Number of partitions of the topic."""
    replicas: int | None = None
    """Number of replicas of the topic."""
    topic_configuration: dict[str, Any] | None = None
    """Topic configuration properties."""


@dataclass(slots=True)
class KafkaMessageBinding(Binding):
    """Kafka message binding describing the key and schema id."""

    key: dict[str, Any] | bool | None = None
    """Schema of the message key."""
    schema_id_location: str | None = None
    """Where the schema id is stored: ``header`` or ``payload``."""
    schema_id_payload_encoding: str | None = None
    """Number of bytes, or the vendor value, used for a schema id in the payload."""
    schema_lookup_strategy: str | None = None
    """Strategy for looking up the schema in the registry."""
