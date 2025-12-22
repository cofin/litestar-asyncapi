from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pytest

from litestar_asyncapi.spec.base import BaseSchemaObject

if TYPE_CHECKING:
    from typing import Any

pytestmark = pytest.mark.anyio


@dataclass(slots=True)
class _Dummy(BaseSchemaObject):
    snake_case: int
    ref: str
    schema_type: str
    parameter_in: str
    aliased: str = field(metadata={"alias": "x-aliased"})
    nested: "_Dummy | None" = None
    items: "list[Any] | None" = None


def test_to_schema_normalizes_keys_and_values() -> None:
    dummy = _Dummy(
        snake_case=1,
        ref="#/components/schemas/Foo",
        schema_type="object",
        parameter_in="query",
        aliased="x",
        items=[{"a_b": 1}, 2],
    )

    schema = dummy.to_schema()
    assert schema["snakeCase"] == 1
    assert schema["$ref"] == "#/components/schemas/Foo"
    assert schema["type"] == "object"
    assert schema["in"] == "query"
    assert schema["x-aliased"] == "x"
    assert schema["items"] == [{"a_b": 1}, 2]


def test_to_schema_serializes_nested_objects() -> None:
    nested = _Dummy(
        snake_case=2,
        ref="#/components/schemas/Bar",
        schema_type="string",
        parameter_in="path",
        aliased="y",
    )
    dummy = _Dummy(
        snake_case=1,
        ref="#/components/schemas/Foo",
        schema_type="object",
        parameter_in="query",
        aliased="x",
        nested=nested,
    )

    schema = dummy.to_schema()
    assert schema["nested"]["snakeCase"] == 2
    assert schema["nested"]["$ref"] == "#/components/schemas/Bar"
