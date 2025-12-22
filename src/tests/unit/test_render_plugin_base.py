import pytest

from litestar_asyncapi.plugins import AsyncAPIRenderPlugin

pytestmark = pytest.mark.anyio


class _DummyPlugin(AsyncAPIRenderPlugin):
    __slots__ = ()

    def render(self, request: object, asyncapi_schema: dict[str, object]) -> bytes:
        return b"ok"


def test_render_plugin_paths_and_has_path() -> None:
    plugin = _DummyPlugin(path="/", media_type="text/plain")
    assert plugin.paths == ["/"]
    assert plugin.has_path("/") is True
    assert plugin.has_path("/missing") is False


def test_render_plugin_accepts_multiple_paths() -> None:
    plugin = _DummyPlugin(path=("/a", "/b"), media_type="text/plain")
    assert plugin.paths == ["/a", "/b"]
    assert plugin.has_path("/b") is True
