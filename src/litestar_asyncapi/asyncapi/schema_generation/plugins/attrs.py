from typing import TYPE_CHECKING, Any, get_type_hints

from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import Reference, Schema, SchemaType
from litestar_asyncapi.typing import ATTRS_INSTALLED, attrs_fields, attrs_has, attrs_nothing

if TYPE_CHECKING:
    from litestar_asyncapi.asyncapi.schema_generation.schema import AsyncAPISchemaGenerator

__all__ = ("AttrsSchemaPlugin",)


class AttrsSchemaPlugin:
    __slots__ = ()

    @staticmethod
    def supports(field_definition: FieldDefinition) -> bool:
        annotation = field_definition.annotation
        return ATTRS_INSTALLED and isinstance(annotation, type) and attrs_has(annotation)

    @staticmethod
    def populate_component_schema(
        *,
        schema: Schema,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> None:
        model = field_definition.annotation
        type_hints = get_type_hints(model, include_extras=True)

        schema.type = SchemaType.OBJECT
        schema.properties = {}
        required: list[str] = []

        for f in attrs_fields(model):
            field_type = type_hints.get(f.name, Any)
            child_field = FieldDefinition.from_annotation(field_type, name=f.name)
            schema.properties[f.name] = generator.generate_schema(child_field)

            has_default = f.default is not attrs_nothing
            if not has_default:
                required.append(f.name)

        schema.required = required or None

    @staticmethod
    def create_inline_schema(
        *,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> Schema | Reference:
        component_schema = Schema()
        AttrsSchemaPlugin.populate_component_schema(
            schema=component_schema,
            field_definition=field_definition,
            generator=generator,
        )
        return component_schema
