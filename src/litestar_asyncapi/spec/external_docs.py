from dataclasses import dataclass

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("ExternalDocumentation",)


@dataclass(slots=True)
class ExternalDocumentation(BaseSchemaObject):
    """Reference external documentation."""

    url: str
    description: str | None = None
