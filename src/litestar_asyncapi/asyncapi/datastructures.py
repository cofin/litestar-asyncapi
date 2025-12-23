import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from litestar.exceptions import ImproperlyConfiguredException
from litestar.params import KwargDefinition
from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import CorrelationId, Message, OperationAction, Parameter, Reference, Schema

__all__ = (
    "DiscoveredChannel",
    "DiscoveredMessage",
    "DiscoveredOperation",
    "DiscoverySource",
    "RegisteredSchema",
    "SchemaRegistry",
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


INVALID_KEY_CHARACTER_PATTERN = re.compile(r"[^a-zA-Z0-9._-]+")


def _longest_common_prefix(tuples_: list[tuple[str, ...]]) -> tuple[str, ...]:
    prefix_ = tuples_[0]
    for t in tuples_:
        prefix_ = prefix_[: min(len(prefix_), len(t))]
        for i in range(len(prefix_)):
            if prefix_[i] != t[i]:
                prefix_ = prefix_[:i]
                break
    return prefix_


def _get_component_key_override(field: FieldDefinition) -> str | None:
    kwarg_definition = field.kwarg_definition
    if not kwarg_definition:
        return None
    if not isinstance(kwarg_definition, KwargDefinition):
        return None
    if kwarg_definition.schema_component_key is None:
        return None
    return _normalize_component_key(kwarg_definition.schema_component_key)


def _normalize_component_key(value: str) -> str:
    sanitized = re.sub(INVALID_KEY_CHARACTER_PATTERN, "_", value)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    if not sanitized:
        msg = f"Invalid schema component key override: {value!r}. The value must include at least one valid character."
        raise ImproperlyConfiguredException(msg)
    return sanitized


def _get_normalized_schema_key(field_definition: FieldDefinition) -> tuple[str, ...]:
    if override := _get_component_key_override(field_definition):
        return (override,)

    annotation = field_definition.annotation
    module = getattr(annotation, "__module__", "")
    is_typing_alias = (
        getattr(annotation, "__origin__", None) is not None and getattr(annotation, "__args__", None) is not None
    )
    if is_typing_alias:
        name = str(annotation)
    else:
        name = getattr(annotation, "__qualname__", None) or getattr(annotation, "__name__", None) or str(annotation)
    name = str(name).replace(".<locals>.", ".")
    name = re.sub(INVALID_KEY_CHARACTER_PATTERN, "_", name)
    return (*module.split("."), name) if module else (name,)


@dataclass(slots=True)
class RegisteredSchema:
    key: tuple[str, ...]
    schema: Schema
    references: list[Reference]
    field_definition: FieldDefinition


class DiscoverySource(str, Enum):
    """Identify the source of a discovered channel."""

    WEBSOCKET = "websocket"
    CHANNELS_PLUGIN = "channels-plugin"


@dataclass(slots=True)
class DiscoveredMessage:
    """Internal representation of a discovered message."""

    payload: Schema | Reference | None = None
    name: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    examples: list[Any] | None = None
    headers: Schema | Reference | None = None
    correlation_id: CorrelationId | Reference | None = None
    content_type: str | None = None
    traits: list[str] | None = None

    def to_spec_message(self) -> Message:
        """Create an AsyncAPI Message object.

        Returns:
            A :class:`~litestar_asyncapi.spec.Message` instance.
        """

        return Message(
            name=self.name,
            title=self.title,
            summary=self.summary,
            description=self.description,
            examples=self.examples,
            headers=self.headers,
            payload=self.payload,
            correlation_id=self.correlation_id,
            content_type=self.content_type,
        )


@dataclass(slots=True)
class DiscoveredOperation:
    """Internal representation of a discovered operation."""

    action: OperationAction
    message: DiscoveredMessage | None = None
    operation_id: str | None = None
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    traits: list[str] | None = None


@dataclass(slots=True)
class DiscoveredChannel:
    """Internal representation of a discovered AsyncAPI channel."""

    address: str
    source: DiscoverySource
    parameters: dict[str, Parameter] | None = None
    operations: "Sequence[DiscoveredOperation]" = ()


class SchemaRegistry:
    """Registry for component schemas with `$ref` deduplication.

    This mirrors Litestar OpenAPI's approach: stable keys for types, reference tracking, and
    shortest-unique component key naming.
    """

    __slots__ = ("_component_type_map", "_model_name_groups", "_schema_key_map", "_schema_reference_map")

    def __init__(self) -> None:
        self._schema_key_map: dict[tuple[str, ...], RegisteredSchema] = {}
        self._schema_reference_map: dict[int, RegisteredSchema] = {}
        self._model_name_groups: defaultdict[str, list[RegisteredSchema]] = defaultdict(list)
        self._component_type_map: dict[tuple[str, ...], FieldDefinition] = {}

    def get_schema_for_field_definition(self, field: FieldDefinition) -> Schema:
        key = _get_normalized_schema_key(field)
        if key not in self._schema_key_map:
            registered = RegisteredSchema(key=key, schema=Schema(), references=[], field_definition=field)
            self._schema_key_map[key] = registered
            self._model_name_groups[key[-1]].append(registered)
            self._component_type_map[key] = field
        else:
            existing_type = self._component_type_map[key]
            if existing_type != field:
                msg = (
                    f"Schema component keys must be unique. Cannot override existing key {'_'.join(key)!r} for type "
                    f"{existing_type.raw!r} with new type {field.raw!r}"
                )
                raise ImproperlyConfiguredException(msg)
        return self._schema_key_map[key].schema

    def get_reference_for_field_definition(self, field: FieldDefinition) -> Reference | None:
        key = _get_normalized_schema_key(field)
        if key not in self._schema_key_map:
            return None

        existing_type = self._component_type_map[key]
        if existing_type != field:
            msg = (
                f"Schema component keys must be unique. While obtaining a reference for the type '{field.raw!r}', the "
                f"generated key {'_'.join(key)!r} was already associated with a different type '{existing_type.raw!r}'. "
            )
            if key_override := _get_component_key_override(field):
                msg += f"Hint: Both types are defining a 'schema_component_key' with the value of {key_override!r}"
            raise ImproperlyConfiguredException(msg)

        registered_schema = self._schema_key_map[key]
        reference = Reference(ref=f"#/components/schemas/{'_'.join(key)}")
        registered_schema.references.append(reference)
        self._schema_reference_map[id(reference)] = registered_schema
        return reference

    def __iter__(self) -> "Iterator[RegisteredSchema]":
        return iter(self._schema_key_map.values())

    @staticmethod
    def _set_reference_paths(name: str, registered_schema: RegisteredSchema) -> None:
        for reference in registered_schema.references:
            reference.ref = f"#/components/schemas/{name}"

    @staticmethod
    def _remove_common_prefix(tuples_: list[tuple[str, ...]]) -> list[tuple[str, ...]]:
        prefix = _longest_common_prefix(tuples_)
        prefix_length = len(prefix)
        return [t[prefix_length:] for t in tuples_]

    def generate_components_schemas(self) -> dict[str, Schema]:
        components_schemas: dict[str, Schema] = {}

        for name, name_group in self._model_name_groups.items():
            if len(name_group) == 1:
                self._set_reference_paths(name, name_group[0])
                components_schemas[name] = name_group[0].schema
                continue

            full_keys = [registered_schema.key for registered_schema in name_group]
            names = ["_".join(k) for k in self._remove_common_prefix(full_keys)]
            for name_, registered_schema in zip(names, name_group, strict=True):
                self._set_reference_paths(name_, registered_schema)
                components_schemas[name_] = registered_schema.schema

        return components_schemas
