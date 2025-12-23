import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_msgspec_schema_is_componentized_and_required_fields_detected() -> None:
    msgspec = pytest.importorskip("msgspec")

    class Event(msgspec.Struct):  # type: ignore[misc,name-defined]
        id: int
        kind: str
        note: str = "default"

    gen = AsyncAPISchemaGenerator()
    ref = gen.generate_schema(FieldDefinition.from_annotation(Event))
    assert isinstance(ref, Reference)

    components = gen.schema_registry.generate_components_schemas()
    key = next(k for k in components if k.endswith("Event"))
    schema = components[key]
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.OBJECT
    assert schema.required == ["id", "kind"]
