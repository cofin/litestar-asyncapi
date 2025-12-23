from dataclasses import dataclass

import pytest
from litestar.typing import FieldDefinition

from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.spec import Reference, Schema, SchemaType

pytestmark = pytest.mark.anyio


@dataclass(slots=True)
class User:
    id: int
    name: str
    nickname: str | None = None


def test_dataclass_schema_is_componentized_and_registered() -> None:
    gen = AsyncAPISchemaGenerator()
    ref = gen.generate_schema(FieldDefinition.from_annotation(User))
    assert isinstance(ref, Reference)

    components = gen.schema_registry.generate_components_schemas()
    assert "User" in components
    schema = components["User"]
    assert isinstance(schema, Schema)
    assert schema.type == SchemaType.OBJECT
    assert schema.properties is not None
    assert schema.properties["id"].type == SchemaType.INTEGER  # type: ignore[union-attr]
    assert schema.required == ["id", "name"]
