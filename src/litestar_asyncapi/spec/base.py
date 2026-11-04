from dataclasses import asdict, dataclass, fields, is_dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from litestar.types import Empty

if TYPE_CHECKING:
    from collections.abc import Iterator
    from dataclasses import Field

__all__ = ("UNSET", "BaseSchemaObject")

UNSET = Empty


def _normalize_key(field_: "Field[Any]") -> str:
    """Return the spec dictionary key for a dataclass field.

    An explicit ``metadata["alias"]`` always wins. Otherwise ``ref`` becomes
    ``$ref`` and snake_case names become camelCase.

    Args:
        field_: The dataclass field.

    Returns:
        The key used in serialized output.

    Raises:
        TypeError: If the field declares a non-string alias.
    """
    if "alias" in field_.metadata:
        alias = field_.metadata["alias"]
        if not isinstance(alias, str):
            msg = 'metadata["alias"] must be a str'
            raise TypeError(msg)
        return alias
    if field_.name == "ref":
        return "$ref"
    first, *rest = field_.name.split("_")
    return first + "".join(component.title() for component in rest)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, BaseSchemaObject):
        return value.to_schema()
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _normalize_value(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {_normalize_value(k): _normalize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(v) for v in value]
    return value.value if isinstance(value, Enum) else value


@dataclass
class BaseSchemaObject:
    """Base class for AsyncAPI spec objects."""

    __slots__ = ()

    @property
    def _exclude_fields(self) -> set[str]:
        return set()

    def _iter_fields(self) -> "Iterator[Field[Any]]":
        yield from fields(self)

    def to_schema(self) -> dict[str, Any]:
        """Serialize the object to a JSON/YAML ready dictionary.

        Serialization rules:
        - omit absent optional fields while preserving explicit nullable literals
        - normalize keys to AsyncAPI/JSON Schema conventions (camelCase, `$ref`, etc.)
        - serialize nested spec objects recursively

        Returns:
            A dictionary representation of the object.

        Raises:
            TypeError: If a field declares an invalid alias metadata value.
            ValueError: If an extension key is not prefixed with ``x-``.
        """
        result: dict[str, Any] = {}
        exclude = self._exclude_fields

        for field_ in self._iter_fields():
            if field_.name in exclude or field_.name == "extensions":
                continue

            raw_value = getattr(self, field_.name)
            if raw_value is UNSET or (raw_value is None and not field_.metadata.get("nullable")):
                continue

            result[_normalize_key(field_)] = _normalize_value(raw_value)

        for key, value in getattr(self, "extensions", {}).items():
            if not isinstance(key, str) or not key.startswith("x-") or key in result:
                msg = f"Invalid specification extension: {key!r}"
                raise ValueError(msg)
            result[key] = _normalize_value(value)

        return result
