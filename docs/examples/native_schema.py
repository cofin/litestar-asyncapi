# /// script
# requires-python = ">=3.10"
# dependencies = ["litestar[standard]", "litestar-asyncapi"]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../.." }
# ///
"""Use a native Litestar schema plugin even when OpenAPI routes are disabled."""

from typing import Any

from litestar import Litestar
from litestar.openapi.spec import OpenAPIType, Schema
from litestar.plugins import OpenAPISchemaPlugin
from litestar.typing import FieldDefinition

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, ChannelDefinition, MessageDefinition, OperationDefinition

__all__ = ("Ticket", "TicketSchemaPlugin", "app")


class Ticket:
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value


class TicketSchemaPlugin(OpenAPISchemaPlugin):
    __slots__ = ()

    def is_plugin_supported_field(self, field_definition: FieldDefinition) -> bool:
        return field_definition.annotation is Ticket

    def to_openapi_schema(self, field_definition: FieldDefinition, schema_creator: Any) -> Schema:
        return Schema(type=OpenAPIType.STRING, pattern="^T-[0-9]+$")


config = AsyncAPIConfig(
    channels=[
        ChannelDefinition(
            key="tickets",
            address="tickets",
            operations=[
                OperationDefinition(
                    action="send",
                    messages=[MessageDefinition(name="Ticket", payload=Ticket, examples=[Ticket("T-42")])],
                )
            ],
        )
    ]
)
app = Litestar(
    openapi_config=None,
    type_encoders={Ticket: lambda ticket: ticket.value},
    plugins=[TicketSchemaPlugin(), AsyncAPIPlugin(config)],
)
