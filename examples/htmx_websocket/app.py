import json
from html import escape
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from litestar import Litestar, Response, get, websocket
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("htmx_socket", "playground")


@websocket("/ws/htmx")
async def htmx_socket(socket: "WebSocket") -> None:
    while True:
        raw = await socket.receive_text()
        message = _extract_message(raw)
        html = (
            '<div id="messages" hx-swap-oob="beforeend">'
            f"<article><strong>Client:</strong> {escape(message)}</article>"
            "</div>"
        )
        await socket.send_text(html)


def _extract_message(raw: str) -> str:
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict) and "message" in payload:
            return str(payload["message"])
    except json.JSONDecodeError:
        pass

    parsed = parse_qs(raw)
    if parsed.get("message"):
        return parsed["message"][0]

    return raw


@get("/", sync_to_thread=False)
def playground() -> Response:
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>HTMX WebSocket Playground</title>
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
        <style>
          body { padding: 2rem; }
          #messages article { margin-bottom: 0.75rem; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>HTMX WebSocket Playground</h1>
          <p>Uses HTMX WebSocket extension to send messages and receive HTML fragments.</p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>

          <div hx-ext="ws" ws-connect="/ws/htmx">
            <form ws-send>
              <label for="message">Message</label>
              <input id="message" name="message" type="text" placeholder="Say hello" required />
              <button type="submit">Send</button>
            </form>
            <section id="messages"></section>
          </div>
        </main>

        <script src="https://unpkg.com/htmx.org@1.9.12"></script>
        <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/ws.js"></script>
      </body>
    </html>
    """
    return Response(html.strip(), media_type=MediaType.HTML)


app = Litestar(route_handlers=[playground, htmx_socket], plugins=[AsyncAPIPlugin()])
