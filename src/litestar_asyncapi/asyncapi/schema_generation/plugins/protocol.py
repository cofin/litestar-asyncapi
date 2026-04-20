from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from litestar.typing import FieldDefinition

    from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
    from litestar_asyncapi.spec import Reference, Schema


class AsyncAPISchemaPluginProtocol(Protocol):
    """Protocol for schema generator plugins."""

    def supports(self, field_definition: "FieldDefinition") -> bool:
        """Return True if this plugin can handle the field definition."""
        ...

    def populate_component_schema(
        self, *, schema: "Schema", field_definition: "FieldDefinition", generator: "AsyncAPISchemaGenerator"
    ) -> None:
        """Populate the provided component schema in-place."""
        ...

    def create_inline_schema(
        self, *, field_definition: "FieldDefinition", generator: "AsyncAPISchemaGenerator"
    ) -> "Schema | Reference":
        """Create an inline schema for a field definition (no component registration)."""
        ...
