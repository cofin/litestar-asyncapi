import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


def test_attrs_schema_is_componentized() -> None:
    attrs = pytest.importorskip("attrs")

    @attrs.define
    class User:
        id: int
        name: str
        nickname: str | None = None

    gen = AsyncAPISchemaGenerator()
    ref = gen.generate_schema(FieldDefinition.from_annotation(User))
    assert isinstance(ref, Reference)

    components = gen.schema_registry.generate_components_schemas()
    key = next(k for k in components if k.endswith("User"))
    schema = components[key]
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.OBJECT
    assert schema.required == ["id", "name"]
