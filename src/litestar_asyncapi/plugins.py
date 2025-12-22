import html
import json
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

import msgspec
import yaml  # type: ignore[import-untyped]
from litestar.enums import MediaType
from litestar.serialization import encode_json, get_serializer

__all__ = (
    "AsyncAPIRenderPlugin",
    "AsyncAPIUIRenderPlugin",
    "JsonRenderPlugin",
    "YamlRenderPlugin",
)

_favicon_url = "https://cdn.jsdelivr.net/gh/litestar-org/branding@main/assets/Branding%20-%20PNG%20-%20Transparent/Badge%20-%20Blue%20and%20Yellow.png"
_default_favicon = f"<link rel='icon' type='image/png' href='{_favicon_url}'>"
_default_style = "<style>body { margin: 0; padding: 0 }</style>"


if TYPE_CHECKING:
    from litestar.connection import Request
    from litestar.router import Router


class AsyncAPIRenderPlugin(ABC):
    """Base class for AsyncAPI render plugins."""

    __slots__ = ("favicon", "media_type", "paths", "style")

    paths: list[str]

    def __init__(
        self,
        *,
        path: str | Sequence[str],
        media_type: MediaType | str = MediaType.HTML,
        favicon: str = _default_favicon,
        style: str = _default_style,
    ) -> None:
        self.paths = [path] if isinstance(path, str) else list(path)
        self.media_type = media_type
        self.favicon = favicon
        self.style = style

    @staticmethod
    def render_json(request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:
        """Render the AsyncAPI schema as JSON.

        Returns:
            The JSON representation as UTF-8 bytes.
        """
        serializer = get_serializer(request.route_handler.resolve_type_encoders())
        return encode_json(asyncapi_schema, serializer=serializer)

    @abstractmethod
    def render(self, request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:
        """Render the output."""
        raise NotImplementedError

    def receive_router(self, router: "Router") -> None:  # noqa: PLR6301
        """Receive the router used to serve docs routes."""
        return

    def has_path(self, path: str) -> bool:
        """Return ``True`` if the plugin is configured for ``path``."""
        return path in self.paths


class JsonRenderPlugin(AsyncAPIRenderPlugin):
    """Render the AsyncAPI schema as JSON."""

    __slots__ = ()

    def __init__(
        self,
        *,
        path: str | Sequence[str] = "/asyncapi.json",
        media_type: str = "application/vnd.asyncapi+json",
        **kwargs: Any,
    ) -> None:
        super().__init__(path=path, media_type=media_type, **kwargs)

    def render(self, request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:
        return self.render_json(request, asyncapi_schema)


class YamlRenderPlugin(AsyncAPIRenderPlugin):
    """Render the AsyncAPI schema as YAML."""

    __slots__ = ()

    def __init__(
        self,
        *,
        path: str | Sequence[str] = ("/asyncapi.yaml", "/asyncapi.yml"),
        media_type: str = "application/vnd.asyncapi+yaml",
        **kwargs: Any,
    ) -> None:
        super().__init__(path=path, media_type=media_type, **kwargs)

    def render(self, request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:  # noqa: PLR6301
        builtins = msgspec.to_builtins(
            asyncapi_schema,
            enc_hook=get_serializer(request.route_handler.resolve_type_encoders()),
        )
        return cast("bytes", yaml.safe_dump(builtins, default_flow_style=False, sort_keys=False).encode("utf-8"))


class AsyncAPIUIRenderPlugin(AsyncAPIRenderPlugin):
    """Render an HTML UI using AsyncAPI's React component."""

    __slots__ = ("_config", "css_url", "js_url")

    def __init__(
        self,
        *,
        path: str | Sequence[str] = "/",
        js_url: str = "https://unpkg.com/@asyncapi/react-component@2.6.5/browser/standalone/index.js",
        css_url: str = "https://unpkg.com/@asyncapi/react-component@2.6.5/styles/default.min.css",
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(path=path, media_type=MediaType.HTML, **kwargs)
        self.js_url = js_url
        self.css_url = css_url
        self._config = config or {}

    def render(self, request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:
        title = "AsyncAPI"
        if isinstance(asyncapi_schema.get("info"), dict) and isinstance(asyncapi_schema["info"].get("title"), str):
            title = asyncapi_schema["info"]["title"]

        schema_json = json.dumps(asyncapi_schema, ensure_ascii=False).replace("</", "<\\/")
        config_json = json.dumps(self._config, ensure_ascii=False).replace("</", "<\\/")

        escaped_title = html.escape(title, quote=True)

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>{escaped_title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="{self.css_url}" />
            <script src="{self.js_url}" crossorigin></script>
            {self.style}
          </head>
          <body>
            <div id="asyncapi"></div>
            <script>
              const schema = {schema_json};
              const config = {config_json};
              AsyncApiStandalone.render({{ schema, config }}, document.getElementById("asyncapi"));
            </script>
          </body>
        </html>
        """
        return html_content.strip().encode("utf-8")
