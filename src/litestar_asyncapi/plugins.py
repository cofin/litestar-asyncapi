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
    "AsyncAPIPlaygroundRenderPlugin",
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

    def render(self, request: "Request", asyncapi_schema: dict[str, Any]) -> bytes:
        """Render the interactive playground HTML.

        Args:
            request: The incoming request.
            asyncapi_schema: The AsyncAPI schema as a dictionary.

        Returns:
            The playground HTML as UTF-8 bytes.
        """
        title = "AsyncAPI"
        if isinstance(asyncapi_schema.get("info"), dict) and isinstance(asyncapi_schema["info"].get("title"), str):
            title = asyncapi_schema["info"]["title"]

        escaped_title = html.escape(title, quote=True)

        # Extract channels for the selector
        channels = asyncapi_schema.get("channels", {})
        channels_json = json.dumps(channels, ensure_ascii=False).replace("</", "<\\/")

        # Determine theme colors
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

        validation_enabled = "true" if self.enable_validation else "false"

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

              <div class="nav-links">
                <a href="./">AsyncAPI UI</a>
                <a href="./asyncapi.json">JSON</a>
                <a href="./asyncapi.yaml">YAML</a>
              </div>

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

            <script>
              const channels = {channels_json};
              const enableValidation = {validation_enabled};

              // DOM elements
              const channelSelect = document.getElementById("channel-select");
              const channelInfo = document.getElementById("channel-info");
              const statusIndicator = document.getElementById("status");
              const messageInput = document.getElementById("message-input");
              const validationError = document.getElementById("validation-error");
              const logEl = document.getElementById("log");
              const filterSelect = document.getElementById("filter-select");

              // State
              let ws = null;
              let messageHistory = [];

              // Populate channel selector
              Object.keys(channels).forEach(path => {{
                const opt = document.createElement("option");
                opt.value = path;
                opt.textContent = path;
                channelSelect.appendChild(opt);
              }});

              // Update channel info when selection changes
              channelSelect.addEventListener("change", () => {{
                const path = channelSelect.value;
                if (path && channels[path]) {{
                  const ch = channels[path];
                  let info = `<strong>Path:</strong> ${{path}}`;
                  if (ch.description) {{
                    info += `<br><strong>Description:</strong> ${{ch.description}}`;
                  }}
                  if (ch.messages) {{
                    info += `<br><strong>Messages:</strong> ${{Object.keys(ch.messages).join(", ")}}`;
                  }}
                  channelInfo.innerHTML = info;
                  channelInfo.style.display = "block";
                }} else {{
                  channelInfo.style.display = "none";
                }}
              }});

              // Status updates
              function setStatus(status) {{
                statusIndicator.className = "status " + status;
              }}

              // Logging
              function log(message, type = "info") {{
                const time = new Date().toLocaleTimeString();
                const entry = {{ time, message, type }};
                messageHistory.push(entry);
                renderLog();
              }}

              function renderLog() {{
                const filter = filterSelect.value;
                logEl.innerHTML = "";
                messageHistory.forEach(entry => {{
                  if (filter === "all" || filter === entry.type || (filter === "sent" && entry.type === "sent") || (filter === "received" && entry.type === "received")) {{
                    const line = document.createElement("div");
                    line.className = entry.type;
                    line.innerHTML = `<span class="timestamp">${{entry.time}}</span>${{entry.message}}`;
                    logEl.appendChild(line);
                  }}
                }});
                logEl.scrollTop = logEl.scrollHeight;
              }}

              filterSelect.addEventListener("change", renderLog);

              // Validation
              function validateJson(text) {{
                if (!enableValidation) return {{ valid: true }};
                try {{
                  JSON.parse(text);
                  return {{ valid: true }};
                }} catch (e) {{
                  return {{ valid: false, error: e.message }};
                }}
              }}

              messageInput.addEventListener("input", () => {{
                const result = validateJson(messageInput.value);
                validationError.textContent = result.valid ? "" : result.error;
              }});

              // WebSocket connection
              function wsUrl(path) {{
                const scheme = location.protocol === "https:" ? "wss" : "ws";
                return `${{scheme}}://${{location.host}}${{path}}`;
              }}

              document.getElementById("connect-btn").addEventListener("click", () => {{
                const path = channelSelect.value;
                if (!path) {{
                  log("Please select a channel first", "error");
                  return;
                }}
                if (ws && ws.readyState <= 1) {{
                  log("Already connected or connecting", "info");
                  return;
                }}

                setStatus("connecting");
                log(`Connecting to ${{path}}...`, "info");

                ws = new WebSocket(wsUrl(path));
                ws.onopen = () => {{
                  setStatus("connected");
                  log(`Connected to ${{path}}`, "info");
                }};
                ws.onmessage = (e) => {{
                  log(`${{e.data}}`, "received");
                }};
                ws.onclose = () => {{
                  setStatus("disconnected");
                  log("Disconnected", "info");
                  ws = null;
                }};
                ws.onerror = () => {{
                  log("WebSocket error", "error");
                }};
              }});

              document.getElementById("disconnect-btn").addEventListener("click", () => {{
                if (ws) {{
                  ws.close();
                }}
              }});

              // Send message
              document.getElementById("send-btn").addEventListener("click", () => {{
                if (!ws || ws.readyState !== WebSocket.OPEN) {{
                  log("Not connected", "error");
                  return;
                }}
                const text = messageInput.value.trim();
                const result = validateJson(text);
                if (!result.valid) {{
                  log("Invalid JSON: " + result.error, "error");
                  return;
                }}
                ws.send(text);
                log(text, "sent");
              }});

              document.getElementById("clear-input-btn").addEventListener("click", () => {{
                messageInput.value = '{{"type": "message", "data": ""}}';
                validationError.textContent = "";
              }});

              document.getElementById("clear-log-btn").addEventListener("click", () => {{
                messageHistory = [];
                renderLog();
              }});

              document.getElementById("export-btn").addEventListener("click", () => {{
                const data = JSON.stringify(messageHistory, null, 2);
                const blob = new Blob([data], {{ type: "application/json" }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "websocket-history.json";
                a.click();
                URL.revokeObjectURL(url);
              }});
            </script>
          </body>
        </html>
        """
        return html_content.strip().encode("utf-8")
