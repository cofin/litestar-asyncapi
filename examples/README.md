# Examples

Each example is self-contained under its own folder and can be run with Litestar.

## Examples

- `websocket_listener/` – Listener-style WebSocket handler with typed payloads
- `websocket_stream/` – Stream-style WebSocket handler returning an async generator
- `decorator_overrides/` – Using AsyncAPI decorators to override metadata
- `channels_plugin/` – Best-effort ChannelsPlugin discovery
- `htmx_websocket/` – HTMX WebSocket extension example

## Running

Install dependencies and run with your preferred ASGI server. For example:

```bash
uv run uvicorn examples.websocket_listener.app:app --reload

uv run uvicorn examples.websocket_stream.app:app --reload

uv run uvicorn examples.decorator_overrides.app:app --reload

uv run uvicorn examples.channels_plugin.app:app --reload

uv run uvicorn examples.htmx_websocket.app:app --reload

## ChannelsPlugin notes

AsyncAPI discovery for ChannelsPlugin is best-effort. If `create_ws_route_handlers=True`, the generated WebSocket
routes are discovered by the WebSocket extractor. If `create_ws_route_handlers=False`, AsyncAPI uses the plugin’s
declared channels list (internal mapping) to document channels.
```

Adjust the module path to match the example you are running.
