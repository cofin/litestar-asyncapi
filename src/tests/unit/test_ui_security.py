from litestar.connection import Request
from litestar_asyncapi.plugins import AsyncAPIPlaygroundRenderPlugin


def test_playground_renderer_escapes_title() -> None:
    plugin = AsyncAPIPlaygroundRenderPlugin()
    schema = {
        "info": {"title": '"><script>alert(1)</script>', "version": "1.0.0"},
        "channels": {}
    }
    # Mock request
    class MockRequest:
        pass
    
    html_bytes = plugin.render(MockRequest(), schema)
    html_str = html_bytes.decode("utf-8")
    
    assert "<script>alert(1)</script>" not in html_str
    assert "&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html_str


def test_playground_js_escaping() -> None:
    plugin = AsyncAPIPlaygroundRenderPlugin()
    # We want to check if the JS code uses dangerous innerHTML without escaping
    html_bytes = plugin.render(None, {"info": {"title": "test", "version": "1.0.0"}, "channels": {}})
    html_str = html_bytes.decode("utf-8")
    
    # Check for escapeHtml usage
    assert 'escapeHtml(' in html_str
    assert 'line.innerHTML = `<span class="timestamp">${escapeHtml(entry.time)}</span>${escapeHtml(entry.message)}`' in html_str
