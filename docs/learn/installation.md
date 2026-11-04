# Installation

Install the package into the environment of your Litestar application:

=== "uv"

    ```bash
    uv add litestar-asyncapi
    ```

=== "pip"

    ```bash
    pip install litestar-asyncapi
    ```

=== "pdm"

    ```bash
    pdm add litestar-asyncapi
    ```

=== "poetry"

    ```bash
    poetry add litestar-asyncapi
    ```

It supports Python 3.10 to 3.14 and Litestar 2.24 or later. The documentation UI ships inside the wheel, so the application needs neither Node nor a CDN.

## A first application

This application has one WebSocket listener and registers `AsyncAPIPlugin`:

```python
--8<-- "docs/examples/websocket_listener/app.py"
```

Save it as `app.py` and start it with the Litestar CLI:

```bash
litestar --app app:app run
```

From a checkout of this repository, run `uv run litestar --app docs.examples.websocket_listener.app:app run` instead.

## The generated document

Open `http://localhost:8000/asyncapi/` for the documentation UI, or download the document from `http://localhost:8000/asyncapi/asyncapi.json`. Its `channels` section describes the listener:

```json
--8<-- "docs/_generated/fragments/websocket_listener/channels.json"
```

## How it works

The plugin reads the application's routes the first time a document is requested. The listener's `data` parameter describes the messages the application receives, and its return annotation describes the messages it sends. Both refer to schemas that Litestar generates for the DTO's incoming and outgoing shapes, which the document keeps under `components.schemas`.

The channel key and its `address` are both the route path. The `ws` binding and the `x-litestar-source: websocket` extension mark the channel as a native WebSocket route, so tools can tell it apart from ChannelsPlugin routes and Server-Sent Event streams.

`DocsConfig` controls the documentation routes under `/asyncapi`. The JSON document is served as `application/vnd.asyncapi+json`. `DocsConfig(yaml=True)` adds `/asyncapi/asyncapi.yaml` and `/asyncapi/asyncapi.yml`. The example also sets `interactive=True`, which adds a WebSocket console at `/asyncapi/playground`; it is off by default.

The console connects only to servers that the document declares, which is why the example adds a `ws` server for `localhost:8000`. The plugin never turns the request's host name into a server entry.

Documents use AsyncAPI 3.1 by default. Set `AsyncAPIConfig(spec_version="3.0.0")` to generate AsyncAPI 3.0 instead.

## Recap

- Register one `AsyncAPIPlugin` and the application serves its AsyncAPI document and UI under `/asyncapi`.
- Listener annotations become `receive` and `send` messages with generated schemas.
- Next, [Concepts and lifecycle](concepts.md) explains channels, operations and the discovery sources.
