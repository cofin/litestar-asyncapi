"""Public typing helpers and optional-dependency flags.

This module is the supported import location for typing shims and `*_INSTALLED` flags.
Implementation details live in `litestar_asyncapi._typing`.
"""

from litestar_asyncapi._typing import (
    ATTRS_INSTALLED,
    MSGSPEC_INSTALLED,
    PYDANTIC_INSTALLED,
    BaseModel,
    Struct,
    attrs_fields,
    attrs_has,
    attrs_nothing,
)

__all__ = (
    "ATTRS_INSTALLED",
    "MSGSPEC_INSTALLED",
    "PYDANTIC_INSTALLED",
    "BaseModel",
    "Struct",
    "attrs_fields",
    "attrs_has",
    "attrs_nothing",
)
