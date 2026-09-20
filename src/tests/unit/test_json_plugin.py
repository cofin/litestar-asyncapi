import pytest

from litestar_asyncapi.plugins import JsonRenderPlugin

pytestmark = pytest.mark.anyio


def test_json_plugin_defaults() -> None:
    from litestar.openapi.plugins import JsonRenderPlugin as NativeJsonRenderPlugin

    from litestar_asyncapi import DocsConfig

    assert JsonRenderPlugin is NativeJsonRenderPlugin
    plugin = next(plugin for plugin in DocsConfig().render_plugins if isinstance(plugin, JsonRenderPlugin))
    assert plugin.paths == ["/asyncapi.json"]
    assert plugin.media_type == "application/vnd.asyncapi+json"


def test_json_yaml_and_ui_share_app_encoder_normalization() -> None:
    import json
    import re
    from decimal import Decimal
    from uuid import UUID

    import yaml
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
    from litestar_asyncapi.spec import Components, Schema

    class Token:
        def __init__(self, value: str) -> None:
            self.value = value

    literal = {"token": Token("custom"), "decimal": Decimal("1.25"), "uuid": UUID(int=1), "null": None}
    config = AsyncAPIConfig(
        components=Components(schemas={"Literal": Schema(example=literal)}), docs=DocsConfig(yaml=True)
    )
    plugin = AsyncAPIPlugin(config)
    app = Litestar(
        [], plugins=[plugin], openapi_config=None, type_encoders={Token: lambda value: {"encoded": value.value}}
    )
    with TestClient(app) as client:
        json_value = client.get("/asyncapi/asyncapi.json").json()
        yaml_value = yaml.safe_load(client.get("/asyncapi/asyncapi.yaml").text)
        html_value = client.get("/asyncapi/").text
    match = re.search(r"const schema = (.*);", html_value)
    assert match is not None
    assert json.loads(match[1]) == yaml_value == json_value == plugin.get_asyncapi_schema(app)
    assert json_value["components"]["schemas"]["Literal"]["example"] == {
        "token": {"encoded": "custom"},
        "decimal": "1.25",
        "uuid": "00000000-0000-0000-0000-000000000001",
        "null": None,
    }
