import sys
from enum import Enum
from random import Random
from types import SimpleNamespace
from typing import Any, ClassVar, cast, get_args, get_origin, get_type_hints

import msgspec
from faker import Faker
from litestar import Litestar
from litestar._openapi.datastructures import SchemaRegistry
from litestar._openapi.schema_generation.examples import ExampleFactory, _create_field_meta
from litestar._openapi.schema_generation.plugins.struct import StructSchemaPlugin
from litestar._openapi.schema_generation.schema import SchemaCreator
from litestar.openapi.spec import Reference, Schema
from litestar.openapi.spec.base import BaseSchemaObject
from litestar.openapi.spec.enums import OpenAPIType
from litestar.params import KwargDefinition
from litestar.plugins.pydantic.plugins.schema import PydanticSchemaPlugin
from litestar.typing import FieldDefinition
from polyfactory.factories.base import BaseFactory

from litestar_asyncapi.spec.base import _normalize_key

__all__ = ("create_schema_creator", "normalize_native_schema", "resolve_annotation")


class _SchemaCreator(SchemaCreator):
    """Apply narrow wire-shape corrections around Litestar's native type engine."""

    __slots__ = ("_namespaces", "_null_schemas", "_signature_namespace", "null_fields")

    def __init__(self, *, signature_namespace: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._signature_namespace = signature_namespace or {}
        self._namespaces: list[dict[str, Any]] = []
        self.null_fields: dict[int, set[str]] = {}
        self._null_schemas: dict[int, Schema] = {}

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
        if id(schema) in self.null_fields:
            self._null_schemas[id(schema)] = schema
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
        prefer_alias=next(
            (plugin.prefer_alias for plugin in app.plugins.openapi if isinstance(plugin, PydanticSchemaPlugin)), True
        ),
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


def declared_schema_examples(field: FieldDefinition, creator: _SchemaCreator) -> list[Any] | None:
    """Read declared examples without finalizing the native registry's reference names."""
    native = creator.for_field_definition(field)
    if isinstance(native, Reference):
        native = creator.schema_registry.get_schema_for_field_definition(field)
    if native.examples is not None:
        return list(native.examples)
    if native.example is not None:
        return [native.example]
    model_config = getattr(field.type_, "model_config", {})
    extra = model_config.get("json_schema_extra") if isinstance(model_config, dict) else None
    if isinstance(extra, dict) and "examples" in extra:
        return list(extra["examples"])
    return None


def native_example_value(field: FieldDefinition) -> Any:
    """Use an isolated native example factory without reseeding shared random state."""
    faker = Faker()
    faker.seed_instance()

    class IsolatedExampleFactory(ExampleFactory):
        __slots__ = ()
        __random_seed__: ClassVar[Any] = None
        __random__ = Random()
        __faker__ = faker
        __max_collection_length__ = 1
        __min_collection_length__ = 1

        @classmethod
        def _get_or_create_factory(cls, model: type[Any]) -> Any:
            factory = cast("Any", BaseFactory._get_or_create_factory).__func__(cls, model)
            return factory.create_factory(
                model,
                **{
                    **cls._get_config(),
                    "__random_seed__": None,
                    "__set_as_default_factory_for_type__": False,
                    "_get_or_create_factory": classmethod(
                        cast("Any", IsolatedExampleFactory._get_or_create_factory).__func__
                    ),
                },
            )

    return IsolatedExampleFactory.get_field_value(_create_field_meta(field))
