import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, Response, get
from litestar.enums import MediaType
from litestar.handlers.websocket_handlers.stream import websocket_stream

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

__all__ = ("StreamItem", "playground", "stream_items")


@dataclass
class StreamItem:
    value: int


@websocket_stream("/ws/stream", signature_namespace={"StreamItem": StreamItem})
async def stream_items() -> "AsyncGenerator[StreamItem, None]":
    i = 0
    while True:
        yield StreamItem(value=i)
        i += 1
        await asyncio.sleep(1)


@get("/", sync_to_thread=False)
def playground() -> Response[str]:
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>AsyncAPI WebSocket Stream</title>
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
        <style>
          body { padding: 2rem; }
          pre { height: 240px; overflow: auto; background: #0b1021; color: #e2e8f0; padding: 1rem; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>WebSocket Stream Playground</h1>
          <p>
            Connect to <code>/ws/stream</code> and watch the stream. This is a server-driven stream, so the client
            does not send data. For client-to-server messages, use the listener example.
          </p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>

          <div class="grid">
            <button id="connect">Connect</button>
            <button id="disconnect" class="secondary">Disconnect</button>
            <button id="clear" class="secondary">Clear Log</button>
          </div>

          <h2>Log</h2>
          <pre id="log"></pre>
        </main>

        <script>
          const logEl = document.getElementById("log");
          let ws;

          function log(message) {
            logEl.textContent += message + "\\n";
            logEl.scrollTop = logEl.scrollHeight;
          }

          function wsUrl() {
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            return `${scheme}://${location.host}/ws/stream`;
          }

          document.getElementById("connect").addEventListener("click", () => {
            if (ws && ws.readyState <= 1) return;
            ws = new WebSocket(wsUrl());
            ws.onopen = () => log("connected");
            ws.onmessage = (event) => log(`received: ${event.data}`);
            ws.onclose = () => log("disconnected");
            ws.onerror = () => log("error");
          });

          document.getElementById("disconnect").addEventListener("click", () => {
            if (ws) ws.close();
          });

          document.getElementById("clear").addEventListener("click", () => {
            logEl.textContent = "";
          });
        </script>
      </body>
    </html>
    """
    return Response(html.strip(), media_type=MediaType.HTML)


app = Litestar(route_handlers=[playground, stream_items], plugins=[AsyncAPIPlugin()])
