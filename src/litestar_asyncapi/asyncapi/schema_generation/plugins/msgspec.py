from typing import TYPE_CHECKING, Any

from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import Reference, Schema, SchemaType
from litestar_asyncapi.typing import MSGSPEC_INSTALLED, Struct

if TYPE_CHECKING:
    from litestar_asyncapi.asyncapi.schema_generation.schema import AsyncAPISchemaGenerator

__all__ = ("MsgspecSchemaPlugin",)


class MsgspecSchemaPlugin:
    __slots__ = ()

    @staticmethod
    def supports(field_definition: FieldDefinition) -> bool:
        annotation = field_definition.annotation
        return MSGSPEC_INSTALLED and isinstance(annotation, type) and issubclass(annotation, Struct)

    @staticmethod
    def populate_component_schema(
        *,
        schema: Schema,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> None:
        model = field_definition.annotation

        field_names: tuple[str, ...] = getattr(model, "__struct_fields__", ())
        defaults: tuple[Any, ...] = getattr(model, "__struct_defaults__", ())
        annotations: dict[str, Any] = getattr(model, "__annotations__", {})

        required_count = max(0, len(field_names) - len(defaults))

        schema.type = SchemaType.OBJECT
        schema.properties = {}
        required: list[str] = []

        for i, name in enumerate(field_names):
            child_field = FieldDefinition.from_annotation(annotations.get(name, Any), name=name)
            schema.properties[name] = generator.generate_schema(child_field)
            if i < required_count:
                required.append(name)

        schema.required = required or None

    @staticmethod
    def create_inline_schema(
        *,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> Schema | Reference:
        component_schema = Schema()
        MsgspecSchemaPlugin.populate_component_schema(
            schema=component_schema,
            field_definition=field_definition,
            generator=generator,
        )
        return component_schema
