from typing import Any, get_origin

from litestar import Litestar
from litestar.exceptions import ImproperlyConfiguredException
from litestar.typing import FieldDefinition

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

_COMPONENT_PREFIX = "#/components/schemas/"


def _describe(type_or_field: Any) -> str:
    """Return a short description of a payload annotation for error messages.

    Args:
        type_or_field: A payload annotation, field definition or native DTO payload.

    Returns:
        The class name for plain classes, otherwise the annotation's ``repr``.
    """
    annotation = type_or_field
    if isinstance(annotation, NativeDTOPayload):
        annotation = annotation.field
    if isinstance(annotation, FieldDefinition):
        annotation = annotation.annotation
    if isinstance(annotation, type) and get_origin(annotation) is None:
        return annotation.__name__
    return repr(annotation)


def _component_references(value: Any) -> set[str]:
    """Collect the component schema names referenced anywhere in an exported schema.

    Args:
        value: An exported schema value.

    Returns:
        Names of the referenced ``components/schemas`` entries.
    """
    if isinstance(value, list):
        return set().union(*(_component_references(item) for item in value))
    if not isinstance(value, dict):
        return set()
    ref = value.get("$ref")
    names = (
        {ref.removeprefix(_COMPONENT_PREFIX)} if isinstance(ref, str) and ref.startswith(_COMPONENT_PREFIX) else set()
    )
    return names.union(*(_component_references(item) for item in value.values()))


class AsyncAPISchemaGenerator:
    """Generate AsyncAPI schemas through a fresh native Litestar schema registry."""

    __slots__ = ("_app", "_creator", "_outputs")

    def __init__(self, app: Litestar | None = None) -> None:
        self._app = app if app is not None else Litestar([])
        self._creator = create_schema_creator(self._app)
        self._outputs: list[tuple[Any, dict[str, Any], str]] = []

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
            native = (
                type_or_field.create_schema(self._creator)
                if isinstance(type_or_field, NativeDTOPayload)
                else self._creator.for_field_definition(field)
            )
            result = to_asyncapi_schema(normalize_native_schema(native, self._creator.null_fields))
            if isinstance(result, dict):
                origin = f"{_describe(field)} for {provenance or 'direct generation'}"
                self._outputs.append((native, result, origin))
        except (ImproperlyConfiguredException, NameError, TypeError, ValueError) as error:
            detail = f"Cannot generate AsyncAPI payload {_describe(type_or_field)}"
            if provenance:
                detail += f" for {provenance}"
            detail += f": {error.detail if isinstance(error, ImproperlyConfiguredException) else error}"
            raise ImproperlyConfiguredException(detail) from error
        else:
            return result

    def components(self) -> dict[str, Any]:
        """Finalize native component names and update previously returned reference dictionaries."""
        components = self._creator.schema_registry.generate_components_schemas()
        for native, output, _ in self._outputs:
            converted = to_asyncapi_schema(normalize_native_schema(native, self._creator.null_fields))
            if isinstance(converted, dict):
                output.clear()
                output.update(converted)
        normalized = {
            name: normalize_native_schema(schema, self._creator.null_fields) for name, schema in components.items()
        }
        exported: dict[str, Any] = {}
        for name, schema in normalized.items():
            try:
                exported[name] = to_asyncapi_schema(schema)
            except ImproperlyConfiguredException as error:
                raise ImproperlyConfiguredException(self._component_error(name, normalized, error.detail)) from error
        return exported

    def declared_examples(self, type_or_field: Any) -> list[Any] | None:
        """Read native schema example declarations without finalizing components."""
        return declared_schema_examples(resolve_annotation(type_or_field, self._app), self._creator)

    def _component_error(self, name: str, normalized: dict[str, Any], reason: str) -> str:
        """Describe a component export failure with only the payloads that reference it.

        Args:
            name: The component that failed to export.
            normalized: All normalized component schemas, keyed by name.
            reason: The export failure detail.

        Returns:
            The error message.
        """
        reaching = {name}
        size = 0
        while size != len(reaching):
            size = len(reaching)
            reaching |= {other for other, schema in normalized.items() if _component_references(schema) & reaching}
        origins = [origin for _, output, origin in self._outputs if _component_references(output) & reaching]
        detail = f"Cannot export AsyncAPI component {name!r}"
        if origins:
            detail += f" for payload {', '.join(origins)}"
        return f"{detail}: {reason}"
