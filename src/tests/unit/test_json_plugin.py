import pytest

from litestar_asyncapi.plugins import JsonRenderPlugin

pytestmark = pytest.mark.anyio


def test_json_plugin_defaults() -> None:
    plugin = JsonRenderPlugin()
    assert plugin.paths == ["/asyncapi.json"]
    assert plugin.media_type == "application/vnd.asyncapi+json"
