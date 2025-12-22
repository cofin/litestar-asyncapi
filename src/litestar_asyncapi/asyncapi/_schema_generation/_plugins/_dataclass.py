import dataclasses
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, get_type_hints

from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import Reference, Schema, SchemaType

if TYPE_CHECKING:
    from litestar_asyncapi._asyncapi.schema_generation.schema import AsyncAPISchemaGenerator

__all__ = ("DataclassSchemaPlugin",)


class DataclassSchemaPlugin:
    __slots__ = ()

    @staticmethod
    def supports(field_definition: FieldDefinition) -> bool:
        annotation = field_definition.annotation
        return dataclasses.is_dataclass(annotation) and isinstance(annotation, type)

    @staticmethod
    def populate_component_schema(
        *, schema: Schema, field_definition: FieldDefinition, generator: "AsyncAPISchemaGenerator"
    ) -> None:
        model = field_definition.annotation
        type_hints = get_type_hints(model, include_extras=True)

        schema.type = SchemaType.OBJECT
        schema.properties = {}
        required: list[str] = []

        for f in dataclasses.fields(model):
            field_type = type_hints.get(f.name, Any)
            child_field = FieldDefinition.from_annotation(field_type, name=f.name)
            schema.properties[f.name] = generator.generate_schema(child_field)

            has_default = not (f.default is MISSING and f.default_factory is MISSING)  # type: ignore[comparison-overlap]
            if not has_default:
                required.append(f.name)

        schema.required = required or None

    @staticmethod
    def create_inline_schema(
        *, field_definition: FieldDefinition, generator: "AsyncAPISchemaGenerator"
    ) -> Schema | Reference:
        component_schema = Schema()
        DataclassSchemaPlugin.populate_component_schema(
            schema=component_schema, field_definition=field_definition, generator=generator
        )
        return component_schema
