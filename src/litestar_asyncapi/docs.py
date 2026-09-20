"""Named documentation links and filesystem-backed package assets."""

import html
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any

from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.plugins import JsonRenderPlugin, YamlRenderPlugin
from litestar.serialization import encode_json

if TYPE_CHECKING:
    from litestar import Request
    from litestar.openapi.plugins import OpenAPIRenderPlugin

__all__ = ("asset_directory", "bootstrap_html", "renderer_name")


def renderer_name(plugin: "OpenAPIRenderPlugin") -> str:
    """Return the stable documentation route name for a renderer."""
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
    if entry == "playground":
        config["entryUrl"] = request.url_for(names["assets"], file_path="playground.js")
    encoded = encode_json(config).decode("utf-8").replace("<", "\\u003c")
    source = html.escape(request.url_for(names["assets"], file_path="bootstrap.js"), quote=True)
    navigation = " ".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label.upper())}</a>' for label, url in links.items()
    )
    return (
        f'<nav aria-label="Documentation">{navigation}</nav>'
        '<p id="asyncapi-status" role="status" aria-live="polite">Loading documentation…</p>'
        f'<script id="asyncapi-config" type="application/json">{encoded}</script>'
        f'<script src="{source}" defer></script>'
    )
