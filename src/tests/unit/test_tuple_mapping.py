from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator


def test_fixed_tuple_mapping() -> None:
    assert AsyncAPISchemaGenerator().generate(tuple[int, str]) == {
        "type": "array",
        "items": [{"type": "integer"}, {"type": "string"}],
        "minItems": 2,
        "maxItems": 2,
    }


def test_variadic_tuple_mapping() -> None:
    assert AsyncAPISchemaGenerator().generate(tuple[int, ...]) == {"type": "array", "items": {"type": "integer"}}
