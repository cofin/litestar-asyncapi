import pytest
from litestar import Litestar
from litestar.testing import TestClient

from litestar_asyncapi import AsyncAPIPlugin

pytestmark = pytest.mark.anyio


def test_docs_routes_exist_and_have_expected_media_types() -> None:
    app = Litestar(route_handlers=[], plugins=[AsyncAPIPlugin()])

    with TestClient(app=app) as client:
        json_response = client.get("/asyncapi/asyncapi.json")
        assert json_response.status_code == 200
        assert json_response.headers["content-type"].startswith("application/vnd.asyncapi+json")
        assert json_response.json()["asyncapi"] == "3.0.0"

        yaml_response = client.get("/asyncapi/asyncapi.yaml")
        assert yaml_response.status_code == 200
        assert yaml_response.headers["content-type"].startswith("application/vnd.asyncapi+yaml")
        assert "asyncapi:" in yaml_response.text

        ui_response = client.get("/asyncapi/")
        assert ui_response.status_code == 200
        assert ui_response.headers["content-type"].startswith("text/html")
        assert "AsyncApiStandalone.render" in ui_response.text
