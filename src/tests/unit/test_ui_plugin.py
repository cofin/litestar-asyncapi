import pytest

from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin

pytestmark = pytest.mark.anyio


def test_ui_plugin_renders_html() -> None:
    plugin = AsyncAPIUIRenderPlugin()
    schema = {"info": {"title": "Test API"}, "asyncapi": "3.0.0"}
    content = plugin.render(request=None, asyncapi_schema=schema)  # type: ignore[arg-type]

    text = content.decode("utf-8")
    assert "<title>Test API</title>" in text
    assert "AsyncApiStandalone.render" in text
    assert "unpkg.com/@asyncapi/react-component" in text


def test_ui_plugin_escapes_title() -> None:
    plugin = AsyncAPIUIRenderPlugin()
    schema = {"info": {"title": "<script>alert(1)</script>"}, "asyncapi": "3.0.0"}
    content = plugin.render(request=None, asyncapi_schema=schema)  # type: ignore[arg-type]

    text = content.decode("utf-8")
    assert "<title><script>alert(1)</script></title>" not in text
    assert "<title>&lt;script&gt;alert(1)&lt;/script&gt;</title>" in text
