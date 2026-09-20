from typing import Any

from litestar import Litestar
from litestar.exceptions import ImproperlyConfiguredException

from litestar_asyncapi._compat import (
    NativeDTOPayload,
    create_schema_creator,
    declared_schema_examples,
    normalize_native_schema,
    resolve_annotation,
)
from litestar_asyncapi.asyncapi.schema_generation.dialect import to_asyncapi_schema
from litestar_asyncapi.spec import MultiFormatSchema

__all__ = ("AsyncAPISchemaGenerator",)


class AsyncAPISchemaGenerator:
    """Generate AsyncAPI schemas through a fresh native Litestar schema registry."""

    __slots__ = ("_app", "_creator", "_origins", "_outputs")

    def __init__(self, app: Litestar | None = None) -> None:
        self._app = app if app is not None else Litestar([])
        self._creator = create_schema_creator(self._app)
        self._origins: list[str] = []
        self._outputs: list[tuple[Any, dict[str, Any]]] = []

    def generate(self, type_or_field: Any, *, provenance: str | None = None) -> dict[str, Any] | bool:
        """Generate a payload schema, retaining native references until component finalization."""
        if isinstance(type_or_field, MultiFormatSchema):
            return type_or_field.to_schema()
        try:
            field = (
                type_or_field.field
                if isinstance(type_or_field, NativeDTOPayload)
                else resolve_annotation(type_or_field, self._app)
            )
            self._origins.append(f"{field.annotation!r} for {provenance or 'direct generation'}")
            native = (
                type_or_field.create_schema(self._creator)
                if isinstance(type_or_field, NativeDTOPayload)
                else self._creator.for_field_definition(field)
            )
            result = to_asyncapi_schema(normalize_native_schema(native, self._creator.null_fields))
            if isinstance(result, dict):
                self._outputs.append((native, result))
        except (ImproperlyConfiguredException, NameError, TypeError, ValueError) as error:
            detail = f"Cannot generate AsyncAPI payload {type_or_field!r}"
            if provenance:
                detail += f" for {provenance}"
            detail += f": {error}"
            raise ImproperlyConfiguredException(detail) from error
        else:
            return result

    def components(self) -> dict[str, Any]:
        """Finalize native component names and update previously returned reference dictionaries."""
        components = self._creator.schema_registry.generate_components_schemas()
        for native, output in self._outputs:
            converted = to_asyncapi_schema(normalize_native_schema(native, self._creator.null_fields))
            if isinstance(converted, dict):
                output.clear()
                output.update(converted)
        try:
            return {
                name: to_asyncapi_schema(normalize_native_schema(schema, self._creator.null_fields))
                for name, schema in components.items()
            }
        except ImproperlyConfiguredException as error:
            detail = f"Cannot export AsyncAPI components for payloads {', '.join(self._origins)}: {error}"
            raise ImproperlyConfiguredException(detail) from error

    def declared_examples(self, type_or_field: Any) -> list[Any] | None:
        """Read native schema example declarations without finalizing components."""
        return declared_schema_examples(resolve_annotation(type_or_field, self._app), self._creator)
