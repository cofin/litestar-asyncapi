"""Named documentation links and filesystem-backed package assets."""

import html
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any

from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.plugins import JsonRenderPlugin, YamlRenderPlugin
from litestar.serialization import decode_json, encode_json

if TYPE_CHECKING:
    from litestar import Request
    from litestar.openapi.plugins import OpenAPIRenderPlugin

__all__ = ("asset_directory", "bootstrap_html", "renderer_name")


def renderer_name(plugin: "OpenAPIRenderPlugin") -> str:
    """Return the stable documentation route name for a renderer."""
    if getattr(plugin, "role", None) == "playground":
        return "asyncapi:playground"
    if isinstance(plugin, JsonRenderPlugin):
        return "asyncapi:json"
    if isinstance(plugin, YamlRenderPlugin):
        return "asyncapi:yaml"
    return f"asyncapi:{type(plugin).__name__}"


def asset_directory() -> Path:
    """Use installed filesystem resources whose lifetime matches the package.

    Wheels and editable installs expose stable paths. Zip imports are unsupported;
    a short-lived extracted directory cannot safely back a static router.
    """
    directory = files("litestar_asyncapi").joinpath("assets")
    if not isinstance(directory, Path):
        message = "AsyncAPI assets require a filesystem installation, not a zip import"
        raise ImproperlyConfiguredException(message)
    return directory


def bootstrap_html(request: "Request[Any, Any, Any]", *, entry: str, options: dict[str, Any]) -> str:
    """Create escaped links and inert configuration for the external bootstrap."""
    names = request.route_handler.opt["asyncapi_routes"]
    links = {key: request.url_for(name) for key, name in names.items() if key != "assets"}
    config = {"schemaUrl": links["json"], "entry": entry, "options": options}
    styles = ""
    if entry in {"react", "scalar"}:
        try:
            manifest = decode_json((asset_directory() / "ui" / "manifest.json").read_bytes())
            selected = manifest[f"frontend/{entry}.ts"]
            config["entryUrl"] = request.url_for(names["assets"], file_path="ui/" + selected["file"])
            pending = [selected]
            visited: set[str] = set()
            css: set[str] = set()
            while pending:
                item = pending.pop()
                if item["file"] in visited:
                    continue
                visited.add(item["file"])
                css.update(item.get("css", []))
                pending.extend(manifest[key] for key in item.get("imports", []))
            styles = "".join(
                f'<link rel="stylesheet" href="{html.escape(request.url_for(names["assets"], file_path="ui/" + name), quote=True)}">'
                for name in sorted(css)
            )
        except (OSError, KeyError, ValueError):
            styles = '<p role="alert">Packaged documentation assets are missing. Use the JSON download.</p>'
    encoded = encode_json(config).decode("utf-8").replace("<", "\\u003c")
    source = html.escape(request.url_for(names["assets"], file_path="bootstrap.js"), quote=True)
    navigation = " ".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label.upper())}</a>' for label, url in links.items()
    )
    return (
        styles + f'<nav aria-label="Documentation">{navigation}</nav>'
        '<p id="asyncapi-status" role="status" aria-live="polite">Loading documentation… If it does not appear, use the JSON download and check your browser content security settings.</p>'
        f'<script id="asyncapi-config" type="application/json">{encoded}</script>'
        f'<script src="{source}" defer></script>'
    )
