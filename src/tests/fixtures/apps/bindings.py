from dataclasses import dataclass
from typing import Literal

from litestar import Litestar

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.asyncapi.datastructures import ChannelDefinition, MessageDefinition, OperationDefinition
from litestar_asyncapi.spec import (
    Channel,
    Components,
    MessageTrait,
    Operation,
    OperationTrait,
    Reference,
    Schema,
    SchemaType,
    Server,
)
from litestar_asyncapi.spec.bindings import (
    AMQPChannelBinding,
    AMQPMessageBinding,
    KafkaChannelBinding,
    KafkaMessageBinding,
    KafkaServerBinding,
)

__all__ = ("app_3_0", "app_3_1")


@dataclass
class Order:
    order_id: str
    quantity: int


@dataclass
class Job:
    name: str


def create_app(spec_version: Literal["3.0.0", "3.1.0"]) -> Litestar:
    config = AsyncAPIConfig(
        title="Bindings fixture",
        version="1.0.0",
        spec_version=spec_version,
        docs=DocsConfig(enabled=False),
        servers={
            "kafka": Server(
                host="broker.example.com:9092",
                protocol="kafka",
                bindings={
                    "kafka": KafkaServerBinding(
                        schema_registry_url="https://registry.example.com",
                        schema_registry_vendor="confluent",
                        binding_version="0.5.0",
                    )
                },
                extensions={"x-cluster": "primary"},
            ),
            "amqp": Server(host="rabbit.example.com:5672", protocol="amqp"),
        },
        operation_traits={"audited": OperationTrait(summary="Audited", extensions={"x-audit": True})},
        message_traits={"tracked": MessageTrait(content_type="application/json", extensions={"x-tracking": "id"})},
        components=Components(
            channels={"audit": Channel(address="audit", extensions={"x-retention": "7d"})},
            operations={
                "audit": Operation(
                    action="send", channel=Reference("#/components/channels/audit"), extensions={"x-owner": "platform"}
                )
            },
        ),
        channels=[
            ChannelDefinition(
                key="orders",
                address="orders",
                servers=[Reference("#/servers/kafka")],
                bindings={
                    "kafka": KafkaChannelBinding(
                        topic="orders",
                        partitions=3,
                        replicas=2,
                        topic_configuration={"cleanup.policy": ["delete"], "retention.ms": 604800000},
                        binding_version="0.5.0",
                    )
                },
                operations=[
                    OperationDefinition(
                        action="send",
                        operation_id="publishOrder",
                        traits=["audited"],
                        messages=[
                            MessageDefinition(
                                payload=Order,
                                name="order",
                                examples=[Order(order_id="A-1", quantity=2)],
                                traits=["tracked"],
                                bindings={
                                    "kafka": KafkaMessageBinding(
                                        key={"type": "string"},
                                        schema_id_location="payload",
                                        schema_id_payload_encoding="confluent",
                                        schema_lookup_strategy="TopicIdStrategy",
                                        binding_version="0.5.0",
                                    )
                                },
                                extensions={"x-partition-key": "order_id"},
                            )
                        ],
                    )
                ],
            ),
            ChannelDefinition(
                key="positions",
                address="positions",
                servers=[Reference("#/servers/kafka")],
                operations=[
                    OperationDefinition(
                        action="send",
                        operation_id="publishPosition",
                        messages=[
                            MessageDefinition(
                                payload=Schema(
                                    type=SchemaType.ARRAY,
                                    prefix_items=[Schema(type=SchemaType.STRING), Schema(type=SchemaType.NUMBER)],
                                    additional_items=False,
                                    min_items=2,
                                ),
                                name="position",
                                examples=[["truck-7", 12.5]],
                            )
                        ],
                    )
                ],
            ),
            ChannelDefinition(
                key="jobs",
                address="jobs",
                servers=[Reference("#/servers/amqp")],
                bindings={
                    "amqp": AMQPChannelBinding(
                        is_="queue",
                        queue={"name": "jobs", "durable": True, "exclusive": False, "autoDelete": False},
                        binding_version="0.3.0",
                    )
                },
                operations=[
                    OperationDefinition(
                        action="receive",
                        operation_id="consumeJob",
                        messages=[
                            MessageDefinition(
                                payload=Job,
                                name="job",
                                examples=[Job(name="rebuild")],
                                bindings={
                                    "amqp": AMQPMessageBinding(
                                        content_encoding="gzip", message_type="job.created", binding_version="0.3.0"
                                    )
                                },
                                extensions={"x-priority": 5},
                            )
                        ],
                    )
                ],
            ),
        ],
    )
    return Litestar(route_handlers=[], plugins=[AsyncAPIPlugin(config)])


app_3_0 = create_app("3.0.0")
app_3_1 = create_app("3.1.0")
