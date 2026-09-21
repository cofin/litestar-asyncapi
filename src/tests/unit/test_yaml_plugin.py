import pytest

from litestar_asyncapi.plugins import YamlRenderPlugin

pytestmark = pytest.mark.anyio


def test_yaml_plugin_defaults() -> None:
    from litestar.openapi.plugins import YamlRenderPlugin as NativeYamlRenderPlugin

    from litestar_asyncapi import DocsConfig

    assert YamlRenderPlugin is NativeYamlRenderPlugin
    plugin = next(plugin for plugin in DocsConfig(yaml=True).render_plugins if isinstance(plugin, YamlRenderPlugin))
    assert plugin.paths == ["/asyncapi.yaml", "/asyncapi.yml"]
    assert plugin.media_type == "application/vnd.asyncapi+yaml"


def test_yaml_route_is_opt_in() -> None:
    from litestar import Litestar
    from litestar.testing import TestClient

    from litestar_asyncapi import AsyncAPIPlugin

    with TestClient(Litestar([], plugins=[AsyncAPIPlugin()])) as client:
        assert client.get("/asyncapi/asyncapi.json").status_code == 200
        assert client.get("/asyncapi/").status_code == 200
        assert client.get("/asyncapi/asyncapi.yaml").status_code == 404
