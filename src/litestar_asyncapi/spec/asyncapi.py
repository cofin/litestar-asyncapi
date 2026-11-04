from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from litestar_asyncapi.spec.base import BaseSchemaObject
from litestar_asyncapi.spec.components import Components

if TYPE_CHECKING:
    from litestar_asyncapi.spec.channel import Channel
    from litestar_asyncapi.spec.info import Info
    from litestar_asyncapi.spec.operation import Operation
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.server import Server

__all__ = ("AsyncAPI",)


@dataclass(slots=True)
class AsyncAPI(BaseSchemaObject):
    """AsyncAPI root document."""

    info: "Info"
    """Metadata about the API."""

    asyncapi: Literal["3.0.0", "3.1.0"] = "3.1.0"
    """AsyncAPI specification version of the document."""
    id: str | None = None
    """Identifier of the application the document describes, as a URI."""
    default_content_type: str | None = None
    """Media type used by messages that declare none."""

    servers: "dict[str, Server | Reference]" = field(default_factory=dict)
    """Servers keyed by name."""
    channels: "dict[str, Channel | Reference]" = field(default_factory=dict)
    """Channels keyed by channel key."""
    operations: "dict[str, Operation | Reference]" = field(default_factory=dict)
    """Operations keyed by operation id."""
    components: Components = field(default_factory=Components)
    """Reusable objects that the document references."""

    extensions: dict[str, Any] = field(default_factory=dict)
    """Specification extensions; every key must start with ``x-``."""
