import pytest

from litestar_asyncapi.spec import Server, ServerVariable

pytestmark = pytest.mark.anyio


def test_server_serialization() -> None:
    server = Server(
        host="localhost:8000",
        protocol="ws",
        variables={"env": ServerVariable(default="dev", enum=["dev", "prod"])},
    )

    schema = server.to_schema()
    assert schema["host"] == "localhost:8000"
    assert schema["protocol"] == "ws"
    assert schema["variables"]["env"]["default"] == "dev"
    assert schema["variables"]["env"]["enum"] == ["dev", "prod"]
