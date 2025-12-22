from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar import Litestar, Response, get, websocket_listener
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("ChatMessage", "chat_listener", "playground")


@dataclass
class ChatMessage:
    room: str
    text: str


@websocket_listener("/ws/chat", signature_namespace={"ChatMessage": ChatMessage})
async def chat_listener(socket: "WebSocket", data: ChatMessage) -> ChatMessage:
    return ChatMessage(room=data.room, text=f"echo: {data.text}")


@get("/", sync_to_thread=False)
def playground() -> Response:
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>AsyncAPI WebSocket Listener</title>
        <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@2/css/pico.min.css" />
        <style>
          body { padding: 2rem; }
          pre { height: 240px; overflow: auto; background: #0b1021; color: #e2e8f0; padding: 1rem; }
          textarea { min-height: 120px; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>WebSocket Listener Playground</h1>
          <p>Connect to <code>/ws/chat</code> and send JSON payloads.</p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>

          <div class="grid">
            <button id="connect">Connect</button>
            <button id="disconnect" class="secondary">Disconnect</button>
          </div>

          <label for="payload">Payload (JSON)</label>
          <textarea id="payload">{ "room": "general", "text": "hello" }</textarea>
          <button id="send">Send</button>

          <h2>Log</h2>
          <pre id="log"></pre>
        </main>

        <script>
          const logEl = document.getElementById("log");
          const payloadEl = document.getElementById("payload");
          let ws;

          function log(message) {
            logEl.textContent += message + "\\n";
            logEl.scrollTop = logEl.scrollHeight;
          }

          function wsUrl() {
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            return `${scheme}://${location.host}/ws/chat`;
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


app = Litestar(route_handlers=[playground, chat_listener], plugins=[AsyncAPIPlugin()])
