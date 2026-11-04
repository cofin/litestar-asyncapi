from dataclasses import dataclass

from litestar_asyncapi.spec.base import BaseSchemaObject

__all__ = ("Reference",)


@dataclass(slots=True)
class Reference(BaseSchemaObject):
    """A JSON reference (`$ref`) wrapper used throughout the spec."""

    ref: str
    """JSON pointer or URI of the referenced object, serialized as ``$ref``."""
