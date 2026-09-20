import sys
from enum import Enum
from types import SimpleNamespace
from typing import Any, cast, get_args, get_origin, get_type_hints

import msgspec
from litestar import Litestar
from litestar._openapi.datastructures import SchemaRegistry
from litestar._openapi.schema_generation.plugins.struct import StructSchemaPlugin
from litestar._openapi.schema_generation.schema import SchemaCreator
from litestar.openapi.spec import Reference, Schema
from litestar.openapi.spec.base import BaseSchemaObject
from litestar.openapi.spec.enums import OpenAPIType
from litestar.params import KwargDefinition
from litestar.typing import FieldDefinition

from litestar_asyncapi.spec.base import _normalize_key

__all__ = ("create_schema_creator", "normalize_native_schema", "resolve_annotation")


class _SchemaCreator(SchemaCreator):
    """Apply narrow wire-shape corrections around Litestar's native type engine."""

    __slots__ = ("_namespaces", "_signature_namespace", "null_fields")

    def __init__(self, *, signature_namespace: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._signature_namespace = signature_namespace or {}
        self._namespaces: list[dict[str, Any]] = []
        self.null_fields: dict[int, set[str]] = {}

    def process_schema_result(self, field: FieldDefinition, schema: Schema) -> Schema | Reference:
        """Record explicit null defaults before native optional fields lose presence."""
        if field.default is None:
            self.null_fields.setdefault(id(schema), set()).add("default")
            if field.is_const:
                self.null_fields[id(schema)].add("const")
        if isinstance(field.kwarg_definition, KwargDefinition):
            extra = field.kwarg_definition.schema_extra or {}
            for name in ("const", "default"):
                if name in extra and extra[name] is None:
                    self.null_fields.setdefault(id(schema), set()).add(name)
        return super().process_schema_result(field, schema)

    def for_field_definition(self, field_definition: FieldDefinition) -> Schema | Reference:
        """Preserve tuple cardinality from its Python annotation, including empty tuples."""
        if field_definition.is_forward_ref:
            namespace = self._namespaces[-1] if self._namespaces else {}
            carrier = SimpleNamespace(__annotations__={"payload": field_definition.raw})
            resolved = get_type_hints(
                carrier, globalns=namespace, localns=self._signature_namespace, include_extras=True
            )["payload"]
            field_definition = FieldDefinition.from_annotation(
                resolved,
                name=field_definition.name,
                default=field_definition.default,
                extra=field_definition.extra,
                kwarg_definition=field_definition.kwarg_definition,
            )
        annotation = field_definition.annotation
        args = get_args(annotation)
        if (
            get_origin(annotation) is tuple
            and hasattr(annotation, "__args__")
            and not (args and args[-1] is Ellipsis)
            and self.get_plugin_for(field_definition) is None
        ):
            args = () if args == ((),) else args
            schema = Schema(
                type=OpenAPIType.ARRAY,
                prefix_items=[self.for_field_definition(FieldDefinition.from_annotation(arg)) for arg in args] or None,
            )
            result = self.process_schema_result(field_definition, schema)
            schema.min_items = max(len(args), schema.min_items if schema.min_items is not None else len(args))
            schema.max_items = min(len(args), schema.max_items if schema.max_items is not None else len(args))
            if (
                isinstance(field_definition.kwarg_definition, KwargDefinition)
                and field_definition.kwarg_definition.max_items == 0
            ):
                schema.max_items = 0
            return result
        return super().for_field_definition(field_definition)

    def for_plugin(self, field_definition: FieldDefinition, plugin: Any) -> Schema | Reference:
        """Reuse native field schemas while correcting msgspec's array wire layout."""
        annotation = field_definition.type_
        module = sys.modules.get(getattr(annotation, "__module__", ""))
        self._namespaces.append(vars(module) if module is not None else {})
        try:
            result = super().for_plugin(field_definition, plugin)
        finally:
            self._namespaces.pop()
        if (
            isinstance(plugin, StructSchemaPlugin)
            and isinstance(annotation, type)
            and issubclass(annotation, msgspec.Struct)
            and annotation.__struct_config__.array_like
        ):
            schema = self.schema_registry.get_schema_for_field_definition(field_definition)
            if schema.properties is not None:
                info = cast("msgspec.inspect.StructType", msgspec.inspect.type_info(annotation))
                properties = schema.properties
                names = [field.encode_name for field in info.fields]
                if info.tag_field:
                    names.insert(0, info.tag_field)
                schema.type = OpenAPIType.ARRAY
                schema.prefix_items = [properties[name] for name in names] or None
                schema.min_items = max(
                    (index + 1 for index, field in enumerate(info.fields) if field.required), default=0
                ) + bool(info.tag_field)
                if annotation.__struct_config__.forbid_unknown_fields:
                    schema.max_items = len(names)
                schema.properties = None
                schema.required = None
            return self.schema_registry.get_reference_for_field_definition(field_definition) or result
        return result


def create_schema_creator(app: Litestar) -> _SchemaCreator:
    """Create an isolated native registry using the application's schema plugins."""
    return _SchemaCreator(
        plugins=app.plugins.openapi,
        schema_registry=SchemaRegistry(),
        generate_examples=False,
        signature_namespace=app.signature_namespace,
    )


def resolve_annotation(annotation: Any, app: Litestar) -> FieldDefinition:
    """Resolve direct annotation names through the application's signature namespace."""
    if isinstance(annotation, str):
        annotation = app.signature_namespace.get(annotation, annotation)
        if isinstance(annotation, str):
            message = f"Unresolved payload annotation {annotation!r} in application signature namespace"
            raise TypeError(message)
    return annotation if isinstance(annotation, FieldDefinition) else FieldDefinition.from_annotation(annotation)


def normalize_native_schema(value: Any, null_fields: dict[int, set[str]] | None = None) -> Any:
    """Serialize native spec objects without pruning null entries from literal data."""
    if isinstance(value, BaseSchemaObject):
        return {
            field.metadata.get("alias", _normalize_key(field.name)): normalize_native_schema(
                getattr(value, field.name), null_fields
            )
            for field in value._iter_fields()
            if field.name not in value._exclude_fields
            and (getattr(value, field.name) is not None or field.name in (null_fields or {}).get(id(value), set()))
        }
    if isinstance(value, dict):
        return {key: normalize_native_schema(item, null_fields) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_native_schema(item, null_fields) for item in value]
    return value.value if isinstance(value, Enum) else value
