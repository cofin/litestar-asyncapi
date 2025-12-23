from typing import Any

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


def attrs_fields_stub(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
    """Placeholder implementation.

    Returns:
        An empty tuple.
    """

    return ()


def attrs_has_stub(*args: Any, **kwargs: Any) -> bool:
    """Placeholder implementation.

    Returns:
        ``False``.
    """

    return False


class AttrsNothingStub:
    """Placeholder for attrs.NOTHING sentinel value."""

    def __repr__(self) -> str:
        return "NOTHING"


ATTRS_NOTHING_STUB = AttrsNothingStub()


try:
    from attrs import NOTHING as attrs_nothing  # noqa: N811
    from attrs import fields as attrs_fields
    from attrs import has as attrs_has

    ATTRS_INSTALLED = True  # pyright: ignore[reportConstantRedefinition]
except ImportError:
    attrs_fields = attrs_fields_stub
    attrs_has = attrs_has_stub  # type: ignore[assignment]
    attrs_nothing = ATTRS_NOTHING_STUB  # type: ignore[assignment]
    ATTRS_INSTALLED = False  # pyright: ignore[reportConstantRedefinition]


class BaseModelStub:
    """Placeholder implementation for pydantic.BaseModel."""


try:
    from pydantic import BaseModel

    PYDANTIC_INSTALLED = True  # pyright: ignore[reportConstantRedefinition]
except ImportError:
    BaseModel = BaseModelStub  # type: ignore[misc,assignment]
    PYDANTIC_INSTALLED = False  # pyright: ignore[reportConstantRedefinition]


class StructStub:
    """Placeholder implementation for msgspec.Struct."""


try:
    import msgspec

    Struct = msgspec.Struct
    MSGSPEC_INSTALLED = True  # pyright: ignore[reportConstantRedefinition]
except ImportError:
    Struct = StructStub  # type: ignore[misc,assignment]
    MSGSPEC_INSTALLED = False  # pyright: ignore[reportConstantRedefinition]
