from litestar import Litestar
from litestar.testing import TestClient

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin


def test_ui_plugin_renders_html() -> None:
    with TestClient(Litestar([], plugins=[AsyncAPIPlugin(AsyncAPIConfig(title="Test API"))])) as client:
        response = client.get("/asyncapi/")
        assert response.status_code == 200
        assert "Test API" in response.text
        assert 'type="application/json"' in response.text
        assert "assets/bootstrap.js" in response.text
