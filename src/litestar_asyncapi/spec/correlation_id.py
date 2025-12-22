from dataclasses import dataclass
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("CorrelationId",)


@dataclass(slots=True)
class CorrelationId(BaseSchemaObject):
    """Defines how to extract a correlation id from a message."""

    location: str
    description: str | None = None
    extensions: dict[str, Any] | None = None

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"} if self.extensions else set()

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        if self.extensions:
            schema.update(self.extensions)
        return schema
