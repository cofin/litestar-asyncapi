import html
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

from litestar.enums import MediaType
from litestar.openapi.plugins import JsonRenderPlugin, OpenAPIRenderPlugin, YamlRenderPlugin

from litestar_asyncapi.docs import bootstrap_html
from litestar_asyncapi.serialization import normalize_document

if TYPE_CHECKING:
    from litestar.connection import Request

__all__ = ("AsyncAPIRenderPlugin", "AsyncAPIUIRenderPlugin", "JsonRenderPlugin", "YamlRenderPlugin")

AsyncAPIRenderPlugin = OpenAPIRenderPlugin


class AsyncAPIUIRenderPlugin(AsyncAPIRenderPlugin):
    """Render an HTML UI using AsyncAPI's React component."""

    __slots__ = ("_config", "interactive", "renderer", "role")

    def __init__(
        self,
        *,
        path: str | Sequence[str] = "/",
        renderer: Literal["asyncapi", "scalar"] = "asyncapi",
        interactive: bool = False,
        role: Literal["documentation", "playground"] = "documentation",
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if renderer == "scalar" and interactive:
            message = "Scalar does not support interactive WebSockets; use the React console"
            raise ValueError(message)
        kwargs.setdefault("favicon", "")
        super().__init__(path=path, media_type=MediaType.HTML, **kwargs)
        self.interactive = interactive
        self.role = role
        self.renderer = renderer
        self._config = config or {}

    def render(self, request: "Request[Any, Any, Any]", openapi_schema: dict[str, Any]) -> bytes:
        openapi_schema = normalize_document(
            openapi_schema, getattr(getattr(request, "app", None), "type_encoders", None)
        )
        title = "AsyncAPI"
        if isinstance(openapi_schema.get("info"), dict) and isinstance(openapi_schema["info"].get("title"), str):
            title = openapi_schema["info"]["title"]

        bootstrap = bootstrap_html(
            request,
            entry="react" if self.renderer == "asyncapi" else "scalar",
            options={**normalize_document(self._config, request.app.type_encoders), "interactive": self.interactive},
        )
        escaped_title = html.escape(title, quote=True)
        limitation = (
            '<p role="note">Scalar currently omits tuple positions, zero-length bounds and boolean payload schemas. '
            "Use the JSON download for the complete contract.</p>"
            if self.renderer == "scalar"
            else ""
        )

        notice = (
            '<p role="note">Validation is advisory. Send transmits the entered text even when invalid. '
            "The server must enforce its own contract. Configure an explicit ws/wss server and parameter values to connect. "
            "Browser WebSockets cannot send arbitrary authentication headers.</p>"
            if self.interactive
            else ""
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>{escaped_title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            {self.style}
          </head>
          <body>
            {limitation}
            {notice}
            <div id="asyncapi"></div>
            {bootstrap}
          </body>
        </html>
        """
        return html_content.strip().encode("utf-8")
