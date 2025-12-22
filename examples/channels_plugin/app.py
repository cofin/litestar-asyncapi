from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, Response, get, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("EchoPayload", "echo", "playground")


@dataclass
class EchoPayload:
    message: str


@websocket_listener("/ws/echo", signature_namespace={"EchoPayload": EchoPayload})
async def echo(socket: "WebSocket", data: EchoPayload) -> EchoPayload:
    return data


@get("/", sync_to_thread=False)
def playground() -> Response:
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>AsyncAPI ChannelsPlugin</title>
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
        <style>
          body { padding: 2rem; }
          pre { height: 240px; overflow: auto; background: #0b1021; color: #e2e8f0; padding: 1rem; }
          textarea { min-height: 120px; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>ChannelsPlugin Playground</h1>
          <p>
            This example shows ChannelsPlugin discovery and a simple echo WebSocket at <code>/ws/echo</code>.
            The AsyncAPI plugin documents the ChannelsPlugin channels and the WebSocket route.
          </p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>
          <p>
            If you enable <code>create_ws_route_handlers=True</code> on ChannelsPlugin, those generated WebSocket
            routes are discovered via the normal WebSocket extractor instead of the ChannelsPlugin fallback.
          </p>

          <div class="grid">
            <button id="connect">Connect</button>
            <button id="disconnect" class="secondary">Disconnect</button>
          </div>

          <label for="payload">Payload (JSON)</label>
          <textarea id="payload">{ "message": "hello" }</textarea>
          <button id="send">Send</button>

          <h2>Log</h2>
          <pre id="log"></pre>
        </main>

        <script>
          const logEl = document.getElementById("log");
          const payloadEl = document.getElementById("payload");
          let ws;

          function log(message) {
            logEl.textContent += message + "\n";
            logEl.scrollTop = logEl.scrollHeight;
          }

          function wsUrl() {
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            return `${scheme}://${location.host}/ws/echo`;
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

          document.getElementById("send").addEventListener("click", () => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
              log("not connected");
              return;
            }
            const raw = payloadEl.value.trim();
            try {
              JSON.parse(raw);
            } catch (err) {
              log("invalid JSON");
              return;
            }
            ws.send(raw);
            log(`sent: ${raw}`);
          });
        </script>
      </body>
    </html>
    """
    return Response(html.strip(), media_type=MediaType.HTML)


backend = MemoryChannelsBackend()
channels_plugin = ChannelsPlugin(backend, channels=["news", "alerts"], create_ws_route_handlers=False)

app = Litestar(route_handlers=[playground, echo], plugins=[AsyncAPIPlugin(), channels_plugin])
