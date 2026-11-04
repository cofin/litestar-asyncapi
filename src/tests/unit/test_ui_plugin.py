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


def test_default_ui_uses_packaged_assets_without_remote_defaults() -> None:
    with TestClient(Litestar([], plugins=[AsyncAPIPlugin()])) as client:
        response = client.get("/asyncapi/")
        assert "unpkg.com" not in response.text
        assert "cdn.jsdelivr" not in response.text
        assert "fonts.googleapis" not in response.text
        assert "react" in response.text


def test_missing_manifest_preserves_download_and_readable_error(monkeypatch, tmp_path) -> None:
    from litestar_asyncapi import docs

    monkeypatch.setattr(docs, "asset_directory", lambda: tmp_path)
    with TestClient(Litestar([], plugins=[AsyncAPIPlugin()])) as client:
        response = client.get("/asyncapi/")
        assert response.status_code == 200
        assert 'role="alert"' in response.text
        assert "assets are missing" in response.text
        assert client.get("/asyncapi/asyncapi.json").status_code == 200


def test_manifest_is_parsed_once_across_pages(monkeypatch) -> None:
    from pathlib import Path

    from litestar_asyncapi import docs

    reads: list[Path] = []
    read_bytes = Path.read_bytes

    def counting_read_bytes(self: Path) -> bytes:
        if self.name == "manifest.json":
            reads.append(self)
        return read_bytes(self)

    docs._read_manifest.cache_clear()
    monkeypatch.setattr(Path, "read_bytes", counting_read_bytes)
    with TestClient(Litestar([], plugins=[AsyncAPIPlugin()])) as client:
        first = client.get("/asyncapi/").text
        second = client.get("/asyncapi/").text
    assert first == second
    assert "assets/ui/" in first
    assert len(reads) == 1
