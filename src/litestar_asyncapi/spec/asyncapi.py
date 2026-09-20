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

    asyncapi: Literal["3.0.0", "3.1.0"] = "3.1.0"
    id: str | None = None
    default_content_type: str | None = None

    servers: "dict[str, Server | Reference]" = field(default_factory=dict)
    channels: "dict[str, Channel | Reference]" = field(default_factory=dict)
    operations: "dict[str, Operation | Reference]" = field(default_factory=dict)
    components: Components = field(default_factory=Components)

    extensions: dict[str, Any] = field(default_factory=dict)
