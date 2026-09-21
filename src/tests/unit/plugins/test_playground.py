"""Exercise the shared, opt-in documentation console."""

import json
import re

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig


@pytest.mark.parametrize("renderer", ["asyncapi", "scalar"])
def test_shared_opt_in_console(renderer: str) -> None:
    app = Litestar(plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(renderer=renderer, interactive=True)))])
    with TestClient(app) as client:
        page = client.get("/asyncapi/")
        console = client.get("/asyncapi/playground")
        assert page.status_code == console.status_code == 200
        assert "/asyncapi/playground" in page.text
        assert "Validation is advisory" in console.text
        assert "Send transmits the entered text even when invalid" in console.text
        bootstrap = json.loads(
            re.search(r'<script id="asyncapi-config" type="application/json">(.*?)</script>', console.text)[1]
        )
        assert bootstrap["entry"] == "react"
        assert bootstrap["options"]["interactive"] is True
        assert bootstrap["schemaUrl"].endswith("/asyncapi/asyncapi.json")
        assert "new WebSocket" not in console.text


def test_interaction_disabled_by_default() -> None:
    with TestClient(Litestar(plugins=[AsyncAPIPlugin()])) as client:
        assert client.get("/asyncapi/playground").status_code == 404
        assert '"interactive":false' in client.get("/asyncapi/").text


def test_shared_renderer_configuration_is_not_mutated() -> None:
    from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin

    renderer = AsyncAPIUIRenderPlugin()
    enabled = DocsConfig(render_plugins=[renderer], interactive=True)
    disabled = DocsConfig(render_plugins=[renderer])
    assert renderer.interactive is False
    assert len(enabled.render_plugins) == len(disabled.render_plugins) + 1
    with TestClient(Litestar(plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=disabled))])) as client:
        assert '"interactive":false' in client.get("/asyncapi/").text
        assert client.get("/asyncapi/playground").status_code == 404


def test_scalar_cannot_claim_interactive_support() -> None:
    from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin

    with pytest.raises(ValueError, match="Scalar does not support interactive WebSockets"):
        AsyncAPIUIRenderPlugin(renderer="scalar", interactive=True)
