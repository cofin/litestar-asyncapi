import warnings
from typing import TYPE_CHECKING, Any

from litestar import Litestar
from litestar.params import KwargDefinition
from litestar.types import Empty
from litestar.typing import FieldDefinition
from polyfactory.exceptions import ParameterException

from litestar_asyncapi._compat import native_example_value
from litestar_asyncapi.serialization import normalize_value
from litestar_asyncapi.spec import MessageExample
from litestar_asyncapi.spec.base import UNSET

if TYPE_CHECKING:
    from litestar_asyncapi import AsyncAPIConfig

__all__ = ("generate_example", "normalize_examples")


def normalize_examples(values: list[Any], *, app: Litestar) -> list[MessageExample]:
    """Normalize explicit values while preserving typed Message Example metadata."""
    result = []
    for value in values:
        if isinstance(value, MessageExample):
            result.append(
                MessageExample(
                    payload=normalize_value(value.payload, app.type_encoders) if value.payload is not UNSET else UNSET,
                    headers=normalize_value(value.headers, app.type_encoders) if value.headers is not None else None,
                    name=value.name,
                    summary=value.summary,
                )
            )
        else:
            result.append(MessageExample(payload=normalize_value(value, app.type_encoders)))
    return result


def _check_constraints(kwarg: Any) -> None:
    constraints = (
        "min_length",
        "max_length",
        "pattern",
        "gt",
        "ge",
        "lt",
        "le",
        "multiple_of",
        "min_items",
        "max_items",
    )
    if isinstance(kwarg, KwargDefinition) and (
        any(getattr(kwarg, name, None) is not None for name in constraints) or kwarg.schema_extra
    ):
        message = "native example generation does not enforce direct Parameter constraints; supply an explicit example"
        raise ValueError(message)


def generate_example(
    field_definition: FieldDefinition, *, config: "AsyncAPIConfig", app: Litestar | None = None
) -> Any:
    """Generate one wire value, or UNSET when automatic generation is disabled or fails."""
    if not config.create_examples:
        return UNSET
    app = app if app is not None else Litestar([])
    try:
        kwarg = field_definition.kwarg_definition
        if isinstance(kwarg, KwargDefinition) and kwarg.default is not Empty:
            candidate = kwarg.default
        elif field_definition.default is not Empty:
            candidate = field_definition.default
        elif isinstance(kwarg, KwargDefinition) and kwarg.enum:
            candidate = kwarg.enum[0]
        else:
            _check_constraints(kwarg)
            candidate = native_example_value(field_definition)
        return normalize_value(candidate, app.type_encoders)
    except (ParameterException, TypeError, ValueError, RecursionError, NameError) as error:
        warnings.warn(f"Omitting automatic AsyncAPI example for {field_definition.annotation!r}: {error}", stacklevel=2)
        return UNSET
