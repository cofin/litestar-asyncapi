# /// script
# requires-python = ">=3.10"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Explicit broker contracts; declarations do not create a broker client or enforce auth."""

from litestar import Litestar

from litestar_asyncapi import (
    AsyncAPIConfig,
    AsyncAPIPlugin,
    ChannelDefinition,
    DocsConfig,
    MessageDefinition,
    OperationDefinition,
)
from litestar_asyncapi.spec import (
    Components,
    CorrelationId,
    MessageTrait,
    OperationTrait,
    Reference,
    Reply,
    SecurityScheme,
    Server,
)

__all__ = ("app",)

config = AsyncAPIConfig(
    title="Broker request/reply contracts",
    docs=DocsConfig(enabled=False),
    servers={"broker": Server(host="localhost:5672", protocol="amqp")},
    components=Components(security_schemes={"credentials": SecurityScheme(type="userPassword")}),
    message_traits={"correlated": MessageTrait(correlation_id=CorrelationId(location="$message.payload#/request_id"))},
    operation_traits={"observed": OperationTrait(summary="Application receives a command")},
    channels=[
        ChannelDefinition(
            key="commands",
            address="orders.commands",
            operations=[
                OperationDefinition(
                    action="receive",
                    operation_id="acceptOrder",
                    traits=["observed"],
                    security=[Reference("#/components/securitySchemes/credentials")],
                    messages=[
                        MessageDefinition(
                            name="Order",
                            payload={"type": "object", "properties": {"request_id": {"type": "string"}}},
                            traits=["correlated"],
                        )
                    ],
                    reply=Reply(
                        channel=Reference("#/channels/results"),
                        messages=[Reference("#/channels/results/messages/Result")],
                    ),
                )
            ],
        ),
        ChannelDefinition(
            key="results",
            address="orders.results",
            operations=[
                OperationDefinition(action="send", messages=[MessageDefinition(name="Result", payload=dict[str, str])])
            ],
        ),
    ],
)
app = Litestar(plugins=[AsyncAPIPlugin(config)])
