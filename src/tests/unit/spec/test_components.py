import pytest

from litestar_asyncapi.spec import Components, Schema, SchemaType, SecurityScheme, SecuritySchemeType

pytestmark = pytest.mark.anyio


def test_components_serialization() -> None:
    components = Components(
        schemas={"Foo": Schema(type=SchemaType.OBJECT)},
        security_schemes={
            "ApiKeyAuth": SecurityScheme(type=SecuritySchemeType.API_KEY, name="X-API-Key", in_="header"),
        },
    )

    data = components.to_schema()
    assert "schemas" in data
    assert data["schemas"]["Foo"]["type"] == "object"
    assert "securitySchemes" in data
    assert data["securitySchemes"]["ApiKeyAuth"]["type"] == "apiKey"
