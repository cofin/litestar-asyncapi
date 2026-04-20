from dataclasses import asdict, dataclass, fields, is_dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator
    from dataclasses import Field

__all__ = ("BaseSchemaObject",)


def _normalize_key(key: str) -> str:
    """Normalize a dataclass field name into a spec dictionary key.

    Args:
        key: The dataclass field name.

    Returns:
        The normalized key used in serialized output.
    """
    if key.endswith("_in"):
        return "in"
    if key.startswith("schema_"):
        # reserved word escape hatch (mirrors Litestar OpenAPI's approach)
        return key.split("_", maxsplit=1)[1]
    if "_" in key:
        components = key.split("_")
        return components[0] + "".join(component.title() for component in components[1:])
    return "$ref" if key == "ref" else key


def _normalize_value(value: Any) -> Any:
    if isinstance(value, BaseSchemaObject):
        return value.to_schema()
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _normalize_value(v) for k, v in asdict(value).items() if v is not None}
    if isinstance(value, dict):
        return {_normalize_value(k): _normalize_value(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
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
        - omit fields with a value of ``None``
        - normalize keys to AsyncAPI/JSON Schema conventions (camelCase, `$ref`, etc.)
        - serialize nested spec objects recursively

        Returns:
            A dictionary representation of the object.

        Raises:
            TypeError: If a field declares an invalid alias metadata value.
        """
        result: dict[str, Any] = {}
        exclude = self._exclude_fields

        for field_ in self._iter_fields():
            if field_.name in exclude:
                continue

            value = _normalize_value(getattr(self, field_.name, None))
            if value is None:
                continue

            if "alias" in field_.metadata:
                alias = field_.metadata["alias"]
                if not isinstance(alias, str):
                    msg = 'metadata["alias"] must be a str'
                    raise TypeError(msg)
                key = alias
            else:
                key = _normalize_key(field_.name)

            result[key] = value

        return result
