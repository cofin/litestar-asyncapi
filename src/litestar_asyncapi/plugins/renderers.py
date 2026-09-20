import html
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from litestar.enums import MediaType
from litestar.openapi.plugins import JsonRenderPlugin, OpenAPIRenderPlugin, YamlRenderPlugin

from litestar_asyncapi.docs import bootstrap_html
from litestar_asyncapi.serialization import normalize_document

if TYPE_CHECKING:
    from litestar.connection import Request

__all__ = (
    "AsyncAPIPlaygroundRenderPlugin",
    "AsyncAPIRenderPlugin",
    "AsyncAPIUIRenderPlugin",
    "JsonRenderPlugin",
    "YamlRenderPlugin",
)

AsyncAPIRenderPlugin = OpenAPIRenderPlugin


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
        if any(urlsplit(url).scheme not in {"", "http", "https"} for url in (js_url, css_url)):
            message = "Documentation asset URLs must use HTTP(S) or relative paths"
            raise ValueError(message)
        self.js_url = js_url
        self.css_url = css_url
        self._config = config or {}

    def render(self, request: "Request[Any, Any, Any]", openapi_schema: dict[str, Any]) -> bytes:
        openapi_schema = normalize_document(
            openapi_schema, getattr(getattr(request, "app", None), "type_encoders", None)
        )
        title = "AsyncAPI"
        if isinstance(openapi_schema.get("info"), dict) and isinstance(openapi_schema["info"].get("title"), str):
            title = openapi_schema["info"]["title"]

        bootstrap = bootstrap_html(
            request, entry="asyncapi", options=normalize_document(self._config, request.app.type_encoders)
        )
        escaped_title = html.escape(title, quote=True)

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <title>{escaped_title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="{html.escape(self.css_url, quote=True)}" />
            <script src="{html.escape(self.js_url, quote=True)}" crossorigin></script>
            {self.style}
          </head>
          <body>
            <div id="asyncapi"></div>
            {bootstrap}
          </body>
        </html>
        """
        return html_content.strip().encode("utf-8")


class AsyncAPIPlaygroundRenderPlugin(AsyncAPIRenderPlugin):
    """Interactive WebSocket testing playground.

    Provides a UI for testing WebSocket endpoints with:
    - Channel selector from AsyncAPI spec
    - Message composer with JSON validation
    - Message history with timestamps
    - Connection state indicators
    """

    __slots__ = ("enable_validation", "theme")

    def __init__(
        self,
        *,
        path: str | Sequence[str] = "/playground",
        enable_validation: bool = True,
        theme: str = "light",
        **kwargs: Any,
    ) -> None:
        """Initialize the playground render plugin.

        Args:
            path: The URL path(s) for the playground.
            enable_validation: Whether to enable JSON validation before sending.
            theme: The color theme ('light' or 'dark').
            **kwargs: Additional arguments passed to the base class.
        """
        super().__init__(path=path, media_type=MediaType.HTML, **kwargs)
        self.enable_validation = enable_validation
        self.theme = theme

    def render(self, request: "Request[Any, Any, Any]", openapi_schema: dict[str, Any]) -> bytes:
        """Render the interactive playground HTML.

        Args:
            request: The incoming request.
            openapi_schema: The AsyncAPI schema as a dictionary.

        Returns:
            The playground HTML as UTF-8 bytes.
        """
        openapi_schema = normalize_document(
            openapi_schema, getattr(getattr(request, "app", None), "type_encoders", None)
        )
        title = "AsyncAPI"
        if isinstance(openapi_schema.get("info"), dict) and isinstance(openapi_schema["info"].get("title"), str):
            title = openapi_schema["info"]["title"]

        escaped_title = html.escape(title, quote=True)

        bootstrap = bootstrap_html(request, entry="playground", options={"enableValidation": self.enable_validation})
        if self.theme == "dark":
            bg_color = "#1a1a2e"
            text_color = "#e2e8f0"
            card_bg = "#16213e"
            input_bg = "#0f3460"
            border_color = "#3a506b"
            log_bg = "#0b1021"
        else:
            bg_color = "#f8fafc"
            text_color = "#1e293b"
            card_bg = "#ffffff"
            input_bg = "#f1f5f9"
            border_color = "#e2e8f0"
            log_bg = "#0b1021"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <title>{escaped_title} - Playground</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
            <style>
              :root {{
                --bg-color: {bg_color};
                --text-color: {text_color};
                --card-bg: {card_bg};
                --input-bg: {input_bg};
                --border-color: {border_color};
                --log-bg: {log_bg};
              }}
              body {{
                background: var(--bg-color);
                color: var(--text-color);
                padding: 1.5rem;
              }}
              .card {{
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
              }}
              .status {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
              }}
              .status.disconnected {{ background: #ef4444; }}
              .status.connecting {{ background: #f59e0b; }}
              .status.connected {{ background: #22c55e; }}
              .log {{
                height: 300px;
                overflow: auto;
                background: var(--log-bg);
                color: #e2e8f0;
                padding: 1rem;
                font-family: monospace;
                font-size: 0.875rem;
                border-radius: 4px;
              }}
              .log .sent {{ color: #60a5fa; }}
              .log .received {{ color: #4ade80; }}
              .log .error {{ color: #f87171; }}
              .log .info {{ color: #a5b4fc; }}
              .log .timestamp {{ color: #94a3b8; margin-right: 8px; }}
              textarea {{
                min-height: 120px;
                font-family: monospace;
              }}
              .nav-links {{
                margin-bottom: 1rem;
              }}
              .nav-links a {{
                margin-right: 1rem;
              }}
              .controls {{
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
              }}
              .channel-info {{
                background: var(--input-bg);
                padding: 0.5rem;
                border-radius: 4px;
                margin-top: 0.5rem;
                font-size: 0.875rem;
              }}
              .validation-error {{
                color: #ef4444;
                font-size: 0.875rem;
                margin-top: 0.25rem;
              }}
            </style>
          </head>
          <body>
            <main class="container">
              <h1>{escaped_title} - WebSocket Playground</h1>

              <div class="card">
                <h2><span id="status" class="status disconnected"></span>Connection</h2>
                <div class="controls">
                  <select id="channel-select" style="flex: 1;">
                    <option value="">Select a channel...</option>
                  </select>
                  <button id="connect-btn">Connect</button>
                  <button id="disconnect-btn" class="secondary">Disconnect</button>
                </div>
                <div id="channel-info" class="channel-info" style="display: none;"></div>
              </div>

              <div class="card">
                <h2>Message Composer</h2>
                <label for="message-input">Message (JSON)</label>
                <textarea id="message-input">{{"type": "message", "data": "hello"}}</textarea>
                <div id="validation-error" class="validation-error"></div>
                <div class="controls" style="margin-top: 0.5rem;">
                  <button id="send-btn">Send Message</button>
                  <button id="clear-input-btn" class="secondary">Clear</button>
                </div>
              </div>

              <div class="card">
                <h2>Message History</h2>
                <div class="controls">
                  <select id="filter-select">
                    <option value="all">All Messages</option>
                    <option value="sent">Sent Only</option>
                    <option value="received">Received Only</option>
                  </select>
                  <button id="clear-log-btn" class="secondary">Clear Log</button>
                  <button id="export-btn" class="outline">Export</button>
                </div>
                <div id="log" class="log"></div>
              </div>
            </main>

            {bootstrap}
          </body>
        </html>
        """
        return html_content.strip().encode("utf-8")
