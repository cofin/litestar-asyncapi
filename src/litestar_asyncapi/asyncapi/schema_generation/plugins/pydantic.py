from typing import TYPE_CHECKING, Any

from litestar.typing import FieldDefinition

from litestar_asyncapi.spec import Reference, Schema, SchemaType
from litestar_asyncapi.typing import PYDANTIC_INSTALLED, BaseModel

if TYPE_CHECKING:
    from litestar_asyncapi.asyncapi.schema_generation.schema import AsyncAPISchemaGenerator

__all__ = ("PydanticSchemaPlugin",)


class PydanticSchemaPlugin:
    __slots__ = ()

    @staticmethod
    def supports(field_definition: FieldDefinition) -> bool:
        annotation = field_definition.annotation
        return PYDANTIC_INSTALLED and isinstance(annotation, type) and issubclass(annotation, BaseModel)

    @staticmethod
    def populate_component_schema(
        *, schema: Schema, field_definition: FieldDefinition, generator: "AsyncAPISchemaGenerator"
    ) -> None:
        model = field_definition.annotation

        schema.type = SchemaType.OBJECT
        schema.properties = {}
        required: list[str] = []

        # Pydantic v2
        if hasattr(model, "model_fields"):
            for name, f in model.model_fields.items():
                ann = getattr(f, "annotation", Any)
                child_field = FieldDefinition.from_annotation(ann, name=name)
                schema.properties[name] = generator.generate_schema(child_field)
                is_required = getattr(f, "is_required", None)
                if callable(is_required):
                    if is_required():
                        required.append(name)
                elif getattr(f, "default", None) is None and getattr(f, "default_factory", None) is None:
                    # best-effort fallback
                    required.append(name)

        # Pydantic v1
        elif hasattr(model, "__fields__"):
            for name, f in model.__fields__.items():
                ann = getattr(f, "outer_type_", Any)
                child_field = FieldDefinition.from_annotation(ann, name=name)
                schema.properties[name] = generator.generate_schema(child_field)
                if getattr(f, "required", False):
                    required.append(name)

        schema.required = required or None

    @staticmethod
    def create_inline_schema(
        *, field_definition: FieldDefinition, generator: "AsyncAPISchemaGenerator"
    ) -> Schema | Reference:
        component_schema = Schema()
        PydanticSchemaPlugin.populate_component_schema(
            schema=component_schema, field_definition=field_definition, generator=generator
        )
        return component_schema
