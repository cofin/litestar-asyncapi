from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from litestar_asyncapi.spec.external_docs import ExternalDocumentation
    from litestar_asyncapi.spec.message import Message
    from litestar_asyncapi.spec.reference import Reference
    from litestar_asyncapi.spec.schema import Schema
    from litestar_asyncapi.spec.tag import Tag

__all__ = ("Channel", "Parameter")


@dataclass(slots=True)
class Parameter(BaseSchemaObject):
    """A channel parameter extracted from an address template."""

    description: str | None = None
    schema: "Schema | Reference | None" = None
    location: str | None = None
    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        if isinstance(schema.get("schema"), dict):
            schema["schema"] = _filter_parameter_schema(schema["schema"])
        schema.update(self.extensions)
        return schema


def _filter_parameter_schema(schema: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "$ref",
        "type",
        "format",
        "enum",
        "default",
        "examples",
        "description",
    }
    return {key: value for key, value in schema.items() if key in allowed}


@dataclass(slots=True)
class Channel(BaseSchemaObject):
    """AsyncAPI Channel object."""

    address: str

    title: str | None = None
    summary: str | None = None
    description: str | None = None

    messages: "dict[str, Message | Reference] | None" = None
    parameters: "dict[str, Parameter] | None" = None
    servers: "list[Reference] | None" = None

    tags: "list[Tag] | None" = None
    external_docs: "ExternalDocumentation | None" = None
    bindings: dict[str, Any] | None = None

    extensions: dict[str, Any] = field(default_factory=dict)

    @property
    def _exclude_fields(self) -> set[str]:
        return {"extensions"}

    def to_schema(self) -> dict[str, Any]:
        schema = BaseSchemaObject.to_schema(self)
        schema.update(self.extensions)
        return schema
