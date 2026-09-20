import json
import re
from html.parser import HTMLParser

from litestar import Litestar
from litestar.testing import TestClient

from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
from litestar_asyncapi.plugins import AsyncAPIUIRenderPlugin


def test_hostile_titles_urls_and_bootstrap_options_remain_data() -> None:
    hostile = '"><script>alert(1)</script>'
    renderer = AsyncAPIUIRenderPlugin(config={"value": "</script><script>alert(2)</script>"})
    app = Litestar(
        [],
        plugins=[
            AsyncAPIPlugin(AsyncAPIConfig(title=hostile, docs=DocsConfig(render_plugins=[renderer], interactive=True)))
        ],
    )
    with TestClient(app) as client:
        for path in ("/asyncapi/", "/asyncapi/playground"):
            text = client.get(path).text
            assert "<script>alert" not in text
            assert "&quot;&gt;&lt;script&gt;" in text
        text = client.get("/asyncapi/").text
    tags: list[tuple[str, dict[str, str | None]]] = []

    class Parser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            tags.append((tag, dict(attrs)))

    Parser().feed(text)
    assert all(not any(key.startswith("on") for key in attrs) for _, attrs in tags)
    match = re.search(r'<script id="asyncapi-config" type="application/json">(.*?)</script>', text)
    assert match is not None
    assert json.loads(match[1])["options"]["value"] == "</script><script>alert(2)</script>"


def test_external_bootstrap_and_playground_report_errors_without_autoconnect() -> None:
    app = Litestar([], plugins=[AsyncAPIPlugin(AsyncAPIConfig(docs=DocsConfig(interactive=True)))])
    with TestClient(app) as client:
        page = client.get("/asyncapi/playground").text
        assert "new WebSocket" not in page
        assert 'type="application/json"' in page
        bootstrap = client.get("/asyncapi/assets/bootstrap.js").text
        assert "Configure an explicit ws/wss server" in page
        assert "location.host" not in bootstrap
        assert 'status.setAttribute("role", "alert")' in bootstrap
