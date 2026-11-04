from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.channel import Channel, Parameter
    from litestar_asyncapi.spec.correlation_id import CorrelationId
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message, MessageTrait
    from litestar_asyncapi.spec.operation import Operation, OperationTrait
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.reply import Reply, ReplyAddress
    from litestar_asyncapi.spec.schema import MultiFormatSchema, Schema
    from litestar_asyncapi.spec.security_scheme import SecurityScheme
    from litestar_asyncapi.spec.server import Server, ServerVariable
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Components",)


@dataclass(slots=True)
class Components(BaseSchemaObject):
    """AsyncAPI reusable components container."""

    schemas: "dict[str, Schema | Reference | MultiFormatSchema | bool | dict[str, Any]]" = field(default_factory=dict)
    """Reusable payload and header schemas."""
    messages: "dict[str, Message | Reference]" = field(default_factory=dict)
    """Reusable messages."""
    message_traits: "dict[str, MessageTrait | Reference]" = field(default_factory=dict)
    """Reusable message traits."""
    security_schemes: "dict[str, SecurityScheme | Reference]" = field(default_factory=dict)
    """Reusable security schemes."""
    parameters: "dict[str, Parameter | Reference]" = field(default_factory=dict)
    """Reusable channel parameters."""
    correlation_ids: "dict[str, CorrelationId | Reference]" = field(default_factory=dict)
    """Reusable correlation ids."""
    operations: "dict[str, Operation | Reference]" = field(default_factory=dict)
    """Reusable operations."""
    operation_traits: "dict[str, OperationTrait | Reference]" = field(default_factory=dict)
    """Reusable operation traits."""
    channels: "dict[str, Channel | Reference]" = field(default_factory=dict)
    """Reusable channels."""
    servers: "dict[str, Server | Reference]" = field(default_factory=dict)
    """Reusable servers."""
    replies: "dict[str, Reply | Reference]" = field(default_factory=dict)
    """Reusable replies."""
    reply_addresses: "dict[str, ReplyAddress | Reference]" = field(default_factory=dict)
    """Reusable reply addresses."""
    server_variables: "dict[str, ServerVariable | Reference]" = field(default_factory=dict)
    """Reusable server variables."""
    tags: "dict[str, Tag | Reference]" = field(default_factory=dict)
    """Reusable tags."""
    external_docs: "dict[str, ExternalDocumentation | Reference]" = field(default_factory=dict)
    """Reusable external documentation objects."""
    server_bindings: "dict[str, dict[str, Any] | Reference]" = field(default_factory=dict)
    """Reusable server bindings."""
    channel_bindings: "dict[str, dict[str, Any] | Reference]" = field(default_factory=dict)
    """Reusable channel bindings."""
    operation_bindings: "dict[str, dict[str, Any] | Reference]" = field(default_factory=dict)
    """Reusable operation bindings."""
    message_bindings: "dict[str, dict[str, Any] | Reference]" = field(default_factory=dict)
    """Reusable message bindings."""
    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
