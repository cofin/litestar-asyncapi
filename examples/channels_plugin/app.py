from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from litestar import Litestar, Response, get, post, websocket_listener
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.channels.plugin import ChannelsPlugin
from litestar.enums import MediaType

from litestar_asyncapi import AsyncAPIPlugin

if TYPE_CHECKING:
    from litestar import WebSocket

__all__ = ("EchoPayload", "PublishPayload", "echo", "playground", "publish_message")


@dataclass
class EchoPayload:
    message: str


@dataclass
class PublishPayload:
    message: str


@websocket_listener("/ws/echo", signature_namespace={"EchoPayload": EchoPayload})
async def echo(socket: "WebSocket[Any, Any, Any]", data: EchoPayload) -> EchoPayload:
    return data


@post("/publish/{channel:str}")
async def publish_message(channel: str, data: PublishPayload, channels: ChannelsPlugin) -> dict[str, str]:
    """Publish a message to a channel.

    Args:
        channel: The channel name to publish to.
        data: The payload containing the message.
        channels: The ChannelsPlugin instance for publishing.

    Returns:
        Status dict with 'published' status and channel name.
    """
    channels.publish({"message": data.message}, channel)
    return {"status": "published", "channel": channel}


@get("/", sync_to_thread=False)
def playground() -> Response[str]:
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
          pre { height: 200px; overflow: auto; background: #0b1021; color: #e2e8f0; padding: 1rem; }
          .section { margin-bottom: 2rem; padding: 1rem; border: 1px solid #ccc; border-radius: 8px; }
        </style>
      </head>
      <body>
        <main class="container">
          <h1>ChannelsPlugin Playground</h1>
          <p>
            This example demonstrates ChannelsPlugin pub/sub with channels <code>news</code> and <code>alerts</code>.
            Subscribe via WebSocket, then publish messages via HTTP POST.
          </p>
          <p>
            <a href="/asyncapi/" target="_blank" rel="noreferrer">AsyncAPI UI</a> ·
            <a href="/asyncapi/asyncapi.json" target="_blank" rel="noreferrer">AsyncAPI JSON</a> ·
            <a href="/asyncapi/asyncapi.yaml" target="_blank" rel="noreferrer">AsyncAPI YAML</a>
          </p>

          <div class="section">
            <h2>Subscribe to Channel</h2>
            <p>Connect to a channel WebSocket to receive published messages.</p>
            <div class="grid">
              <select id="channel">
                <option value="news">news</option>
                <option value="alerts">alerts</option>
              </select>
              <button id="subscribe">Subscribe</button>
              <button id="unsubscribe" class="secondary">Unsubscribe</button>
            </div>
            <h3>Received Messages</h3>
            <pre id="subscribe-log"></pre>
          </div>

          <div class="section">
            <h2>Publish to Channel</h2>
            <p>Send a message to all subscribers of a channel via HTTP POST.</p>
            <div class="grid">
              <select id="publish-channel">
                <option value="news">news</option>
                <option value="alerts">alerts</option>
              </select>
              <input type="text" id="publish-message" placeholder="Message to publish" value="Hello from the playground!" />
            </div>
            <button id="publish">Publish</button>
            <h3>Publish Log</h3>
            <pre id="publish-log"></pre>
          </div>

          <div class="section">
            <h2>Echo WebSocket</h2>
            <p>Simple echo at <code>/ws/echo</code> (separate from channels).</p>
            <div class="grid">
              <button id="echo-connect">Connect</button>
              <button id="echo-disconnect" class="secondary">Disconnect</button>
            </div>
            <input type="text" id="echo-message" placeholder="Message to echo" value="hello" style="margin-top: 0.5rem;" />
            <button id="echo-send">Send</button>
            <h3>Echo Log</h3>
            <pre id="echo-log"></pre>
          </div>
        </main>

        <script>
          // Subscribe functionality
          let channelWs;
          const subscribeLog = document.getElementById("subscribe-log");

          function logSubscribe(msg) {
            subscribeLog.textContent += msg + "\\n";
            subscribeLog.scrollTop = subscribeLog.scrollHeight;
          }

          document.getElementById("subscribe").addEventListener("click", () => {
            if (channelWs && channelWs.readyState <= 1) {
              logSubscribe("already connected or connecting");
              return;
            }
            const channel = document.getElementById("channel").value;
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            const url = `${scheme}://${location.host}/${channel}`;
            logSubscribe(`connecting to ${url}...`);
            channelWs = new WebSocket(url);
            channelWs.onopen = () => logSubscribe(`subscribed to ${channel}`);
            channelWs.onmessage = (e) => logSubscribe(`[${channel}] ${e.data}`);
            channelWs.onclose = (e) => logSubscribe(`unsubscribed from ${channel} (code: ${e.code})`);
            channelWs.onerror = (e) => logSubscribe(`error: ${e.type}`);
          });

          document.getElementById("unsubscribe").addEventListener("click", () => {
            if (channelWs) channelWs.close();
          });

          // Publish functionality
          const publishLog = document.getElementById("publish-log");

          function logPublish(msg) {
            publishLog.textContent += msg + "\\n";
            publishLog.scrollTop = publishLog.scrollHeight;
          }

          document.getElementById("publish").addEventListener("click", async () => {
            const channel = document.getElementById("publish-channel").value;
            const message = document.getElementById("publish-message").value;
            try {
              const res = await fetch(`/publish/${channel}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
              });
              const data = await res.json();
              logPublish(`published to ${data.channel}: ${message}`);
            } catch (err) {
              logPublish(`error: ${err.message}`);
            }
          });

          // Echo functionality
          let echoWs;
          const echoLog = document.getElementById("echo-log");

          function logEcho(msg) {
            echoLog.textContent += msg + "\\n";
            echoLog.scrollTop = echoLog.scrollHeight;
          }

          document.getElementById("echo-connect").addEventListener("click", () => {
            if (echoWs && echoWs.readyState <= 1) return;
            const scheme = location.protocol === "https:" ? "wss" : "ws";
            echoWs = new WebSocket(`${scheme}://${location.host}/ws/echo`);
            echoWs.onopen = () => logEcho("connected to echo");
            echoWs.onmessage = (e) => logEcho(`echo: ${e.data}`);
            echoWs.onclose = () => logEcho("disconnected");
            echoWs.onerror = () => logEcho("error");
          });

          document.getElementById("echo-disconnect").addEventListener("click", () => {
            if (echoWs) echoWs.close();
          });

          document.getElementById("echo-send").addEventListener("click", () => {
            if (!echoWs || echoWs.readyState !== WebSocket.OPEN) {
              logEcho("not connected");
              return;
            }
            const message = document.getElementById("echo-message").value;
            echoWs.send(JSON.stringify({ message }));
            logEcho(`sent: ${message}`);
          });
        </script>
      </body>
    </html>
    """
    return Response(html.strip(), media_type=MediaType.HTML)


backend = MemoryChannelsBackend()
channels_plugin = ChannelsPlugin(backend, channels=["news", "alerts"], create_ws_route_handlers=True)

app = Litestar(route_handlers=[playground, echo, publish_message], plugins=[AsyncAPIPlugin(), channels_plugin])
