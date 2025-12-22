import pytest

from litestar_asyncapi.spec import Contact, Info, License

pytestmark = pytest.mark.anyio


def test_info_serialization() -> None:
    info = Info(
        title="Test",
        version="1.0.0",
        description="Desc",
        contact=Contact(name="Dev", email="dev@example.com"),
        license=License(name="MIT", url="https://example.com/license"),
    )

    schema = info.to_schema()
    assert schema["title"] == "Test"
    assert schema["version"] == "1.0.0"
    assert schema["description"] == "Desc"
    assert schema["contact"]["email"] == "dev@example.com"
    assert schema["license"]["name"] == "MIT"
