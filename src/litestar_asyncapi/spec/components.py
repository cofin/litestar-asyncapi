from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.channel import Channel, Parameter
    from litestar_asyncapi.spec.correlation_id import CorrelationId
    from litestar_asyncapi.spec.message import Message, MessageTrait
    from litestar_asyncapi.spec.operation import Operation, OperationTrait
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.schema import Schema
    from litestar_asyncapi.spec.security_scheme import SecurityScheme
    from litestar_asyncapi.spec.server import Server

__all__ = ("Components",)


@dataclass(slots=True)
class Components(BaseSchemaObject):
    """AsyncAPI reusable components container."""

    schemas: "dict[str, Schema | Reference]" = field(default_factory=dict)
    messages: "dict[str, Message | Reference]" = field(default_factory=dict)
    message_traits: "dict[str, MessageTrait | Reference]" = field(default_factory=dict)
    security_schemes: "dict[str, SecurityScheme | Reference]" = field(default_factory=dict)
    parameters: "dict[str, Parameter | Reference]" = field(default_factory=dict)
    correlation_ids: "dict[str, CorrelationId | Reference]" = field(default_factory=dict)
    operations: "dict[str, Operation | Reference]" = field(default_factory=dict)
    operation_traits: "dict[str, OperationTrait | Reference]" = field(default_factory=dict)
    channels: "dict[str, Channel | Reference]" = field(default_factory=dict)
    servers: "dict[str, Server | Reference]" = field(default_factory=dict)
