import typing
from typing import TYPE_CHECKING, Any, get_type_hints
from typing import get_origin as typing_get_origin

from litestar.typing import FieldDefinition
from typing_extensions import NotRequired, Required

from litestar_asyncapi.spec import Reference, Schema, SchemaType

if TYPE_CHECKING:
    from litestar_asyncapi.asyncapi.schema_generation.schema import AsyncAPISchemaGenerator

__all__ = ("TypedDictSchemaPlugin",)


class TypedDictSchemaPlugin:
    __slots__ = ()

    @staticmethod
    def supports(field_definition: FieldDefinition) -> bool:
        annotation = field_definition.annotation
        return (
            isinstance(annotation, type) and hasattr(annotation, "__total__") and hasattr(annotation, "__annotations__")
        )

    @staticmethod
    def populate_component_schema(
        *,
        schema: Schema,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> None:
        td = field_definition.annotation
        annotations: dict[str, Any] = getattr(td, "__annotations__", {})

        # Prefer resolving annotations to handle `from __future__ import annotations` in user code.
        try:
            type_hints: dict[str, Any] = get_type_hints(td, include_extras=True)
        except (NameError, TypeError):  # pragma: no cover
            type_hints = annotations

        total: bool = bool(getattr(td, "__total__", True))
        optional_keys: set[str] = set(getattr(td, "__optional_keys__", set()))
        required_keys: set[str] = set(getattr(td, "__required_keys__", set()))

        # Some TypedDict implementations can misreport required/optional keys when annotations are stored as strings.
        # Compute required keys based on `Required`/`NotRequired` wrappers when available.
        inferred_optional: set[str] = set()
        inferred_required: set[str] = set()

        for name, ann in type_hints.items():
            origin = typing_get_origin(ann)
            if origin in {getattr(typing, "NotRequired", NotRequired), NotRequired}:
                inferred_optional.add(name)
            elif origin in {getattr(typing, "Required", Required), Required} or total:
                inferred_required.add(name)
            else:
                inferred_optional.add(name)

        if inferred_optional or inferred_required:
            optional_keys = inferred_optional
            required_keys = inferred_required
        elif optional_keys:
            required_keys = set(type_hints) - optional_keys
        elif not required_keys:
            required_keys = set(type_hints) if total else set()

        schema.type = SchemaType.OBJECT
        schema.properties = {}
        required: list[str] = []

        for name, ann in type_hints.items():
            child_field = FieldDefinition.from_annotation(ann, name=name)
            schema.properties[name] = generator.generate_schema(child_field)
            if name in required_keys:
                required.append(name)

        schema.required = required or None

    @staticmethod
    def create_inline_schema(
        *,
        field_definition: FieldDefinition,
        generator: "AsyncAPISchemaGenerator",
    ) -> Schema | Reference:
        component_schema = Schema()
        TypedDictSchemaPlugin.populate_component_schema(
            schema=component_schema,
            field_definition=field_definition,
            generator=generator,
        )
        return component_schema
