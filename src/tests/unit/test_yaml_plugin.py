import pytest

from litestar_asyncapi.plugins import YamlRenderPlugin

pytestmark = pytest.mark.anyio


def test_yaml_plugin_defaults() -> None:
    plugin = YamlRenderPlugin()
    assert plugin.paths == ["/asyncapi.yaml", "/asyncapi.yml"]
    assert plugin.media_type == "application/vnd.asyncapi+yaml"
