from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject
from litestar_asyncapi.spec.components import Components

if TYPE_CHECKING:
    from litestar_asyncapi.spec.channel import Channel
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.info import Info
    from litestar_asyncapi.spec.operation import Operation
    from litestar_asyncapi.spec.server import Server
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("AsyncAPI",)


@dataclass(slots=True)
class AsyncAPI(BaseSchemaObject):
    """AsyncAPI root document."""

    info: "Info"

    asyncapi: str = "3.0.0"
    id: str | None = None
    default_content_type: str | None = None

    servers: "dict[str, Server]" = field(default_factory=dict)
    channels: "dict[str, Channel]" = field(default_factory=dict)
    operations: "dict[str, Operation]" = field(default_factory=dict)
    components: Components = field(default_factory=Components)

    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
