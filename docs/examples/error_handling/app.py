# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "litestar[standard]",
#     "litestar-asyncapi",
# ]
# [tool.uv.sources]
# litestar-asyncapi = { path = "../../.." }
# ///
"""Error handling example demonstrating WebSocket error scenarios.

This example shows how WebSocket handlers can gracefully handle various
error conditions and how the AsyncAPI documentation reflects the message schemas.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, Response, get, websocket_listener
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("ErrorPayload", "ErrorResponse", "error_demo", "playground")


@dataclass
class ErrorPayload:
    """Payload for triggering error scenarios."""

    action: str
    """Action to perform: 'echo', 'error', or 'validate'."""
    value: str | None = None
    """Optional value for the action."""


@dataclass
class ErrorResponse:
    """Response from the error demo handler."""

    status: str
    """Status of the operation: 'ok' or 'error'."""
    message: str
    """Descriptive message about the result."""
    original_action: str | None = None
    """The action that was requested."""


_INTENTIONAL_ERROR_MSG = "Intentional error triggered by client"


@websocket_listener("/ws/errors", signature_namespace={"ErrorPayload": ErrorPayload, "ErrorResponse": ErrorResponse})
async def error_demo(socket: "WebSocket", data: ErrorPayload) -> ErrorResponse:
    """Handle messages and demonstrate error scenarios.

    Supported actions:
    - 'echo': Echo back the value
    - 'error': Intentionally raise an error
    - 'validate': Validate the value is not empty

    Args:
        socket: The WebSocket connection.
        data: The incoming payload with action and optional value.

    Returns:
        ErrorResponse with status and message.

    Raises:
        ValueError: When action is 'error' to demonstrate error handling.
    """
    if data.action == "echo":
        return ErrorResponse(
            status="ok",
            message=f"Echoed: {data.value}",
            original_action=data.action,
        )
    if data.action == "error":
        raise ValueError(_INTENTIONAL_ERROR_MSG)
    if data.action == "validate":
        if not data.value:
            return ErrorResponse(
                status="error",
                message="Validation failed: value is required",
                original_action=data.action,
            )
        return ErrorResponse(
            status="ok",
            message=f"Validation passed for: {data.value}",
            original_action=data.action,
        )
    return ErrorResponse(
        status="error",
        message=f"Unknown action: {data.action}",
        original_action=data.action,
    )


@get("/", sync_to_thread=False)
def playground() -> Response[str]:
    """Serve the error handling playground HTML.

    Returns:
        HTML response with the playground interface.
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>AsyncAPI Error Handling</title>
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
        <style>
          body { padding: 2rem; }
          pre { height: 280px; overflow: auto; background: #0b1021; color: #e2e8f0; padding: 1rem; }
          .error { color: #f87171; }
          .success { color: #4ade80; }
          .action-btn { margin-right: 0.5rem; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>Error Handling Playground</h1>
          <p>
            This example demonstrates how WebSocket handlers can gracefully handle
            various error conditions. Try different actions to see the responses.
          </p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>

          <div class="grid">
            <button id="connect">Connect</button>
            <button id="disconnect" class="secondary">Disconnect</button>
          </div>

          <h2>Actions</h2>
          <p>Click an action button to send a predefined message:</p>
          <div>
            <button id="action-echo" class="action-btn">Echo</button>
            <button id="action-validate-ok" class="action-btn">Validate (OK)</button>
            <button id="action-validate-fail" class="action-btn">Validate (Fail)</button>
            <button id="action-error" class="action-btn secondary">Trigger Error</button>
            <button id="action-unknown" class="action-btn secondary">Unknown Action</button>
            <button id="action-invalid-json" class="action-btn outline">Invalid JSON</button>
          </div>

          <h2>Custom Message</h2>
          <label for="payload">Payload (JSON)</label>
          <textarea id="payload" style="min-height: 80px;">{ "action": "echo", "value": "hello" }</textarea>
          <button id="send">Send Custom</button>

          <h2>Log</h2>
          <button id="clear" class="outline" style="margin-bottom: 0.5rem;">Clear Log</button>
          <pre id="log"></pre>
        </main>

        <script>
          const logEl = document.getElementById("log");
          const payloadEl = document.getElementById("payload");
          let ws;

          function log(message, type = "info") {
            const prefix = type === "error" ? "[ERROR] " : type === "success" ? "[OK] " : "";
            const span = document.createElement("span");
            span.className = type;
            span.textContent = prefix + message + "\\n";
            logEl.appendChild(span);
            logEl.scrollTop = logEl.scrollHeight;
          }

          function wsUrl() {
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            return `${scheme}://${location.host}/ws/errors`;
          }

          function sendPayload(payload) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
              log("Not connected", "error");
              return;
            }
            const raw = typeof payload === "string" ? payload : JSON.stringify(payload);
            ws.send(raw);
            log(`Sent: ${raw}`);
          }

          document.getElementById("connect").addEventListener("click", () => {
            if (ws && ws.readyState <= 1) return;
            ws = new WebSocket(wsUrl());
            ws.onopen = () => log("Connected to /ws/errors", "success");
            ws.onmessage = (e) => {
              try {
                const data = JSON.parse(e.data);
                const type = data.status === "ok" ? "success" : "error";
                log(`Received: ${e.data}`, type);
              } catch {
                log(`Received: ${e.data}`);
              }
            };
            ws.onclose = () => log("Disconnected");
            ws.onerror = () => log("WebSocket error", "error");
          });

          document.getElementById("disconnect").addEventListener("click", () => {
            if (ws) ws.close();
          });

          document.getElementById("send").addEventListener("click", () => {
            const raw = payloadEl.value.trim();
            try {
              JSON.parse(raw);
              sendPayload(raw);
            } catch (err) {
              log("Invalid JSON in textarea", "error");
            }
          });

          document.getElementById("clear").addEventListener("click", () => {
            logEl.innerHTML = "";
          });

          // Action buttons
          document.getElementById("action-echo").addEventListener("click", () => {
            sendPayload({ action: "echo", value: "Hello, World!" });
          });

          document.getElementById("action-validate-ok").addEventListener("click", () => {
            sendPayload({ action: "validate", value: "valid-value" });
          });

          document.getElementById("action-validate-fail").addEventListener("click", () => {
            sendPayload({ action: "validate", value: null });
          });

          document.getElementById("action-error").addEventListener("click", () => {
            sendPayload({ action: "error" });
          });

          document.getElementById("action-unknown").addEventListener("click", () => {
            sendPayload({ action: "unknown-action" });
          });

          document.getElementById("action-invalid-json").addEventListener("click", () => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
              log("Not connected", "error");
              return;
            }
            ws.send("{ invalid json }");
            log("Sent: { invalid json } (intentionally malformed)");
          });
        </script>
      </body>
    </html>
    """
    return Response(html.strip(), media_type=MediaType.HTML)


app = Litestar(route_handlers=[playground, error_demo], plugins=[AsyncAPIPlugin()])
