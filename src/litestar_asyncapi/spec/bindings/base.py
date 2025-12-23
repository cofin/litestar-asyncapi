from dataclasses import dataclass, field
from typing import Any

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("Binding",)


@dataclass(slots=True)
class Binding(BaseSchemaObject):
    """Base class for protocol binding objects.

    Bindings commonly have a `bindingVersion` field and may include vendor extensions.
    """

    binding_version: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)  # pyright: ignore

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
