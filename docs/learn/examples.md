# Runnable examples

Run these commands from the repository root after `make install`. Each module
contains PEP 723 dependency metadata, but executing the Python file alone does
not launch a server: it constructs the application and exits. The native Litestar CLI
starts the application. The PEP 723 metadata serves dependency-aware tools and points to
this checkout.

The listener, stream, decorator, Channels and error examples expose the shared optional console
at `/asyncapi/playground`; validation there is advisory, and Send can transmit invalid entered text. Open
`/asyncapi` for documentation and connect only to a server you intend to use.

The HTMX example retains its distinct HTML-fragment UI at `/` and loads HTMX/Pico assets from
external CDNs. Broker contracts do not implement a broker transport. All socket authorization and
validation remain application responsibilities.

## WebSocket listener { #websocket-listener }

Typed dataclass input and output. The application receives input and sends its returned value.

```bash
uv run litestar --app docs.examples.websocket_listener.app:app run
```

```python
--8<-- "docs/examples/websocket_listener/app.py"
```

## WebSocket stream { #websocket-stream }

An asynchronous generator emits JSON object events until disconnected.

```bash
uv run litestar --app docs.examples.websocket_stream.app:app run
```

```python
--8<-- "docs/examples/websocket_stream/app.py"
```

## Raw socket and multiple messages { #decorator-overrides }

A raw socket accepts two named message types and returns a JSON result. Explicit metadata supplies its contract.

```bash
uv run litestar --app docs.examples.decorator_overrides.app:app run
```

```python
--8<-- "docs/examples/decorator_overrides/app.py"
```

## Channels and publish endpoint { #channels-plugin }

Actual generated news/alerts subscriber routes plus a POST publish endpoint. Internal subscriptions alone do not become documented routes.

```bash
uv run litestar --app docs.examples.channels_plugin.app:app run
```

```python
--8<-- "docs/examples/channels_plugin/app.py"
```

## HTMX HTML fragments { #htmx-websocket }

A distinct HTML-fragment UI at `/` uses HTMX with external CDN assets. Its text/HTML wire format is documented but unsupported by the JSON console.

```bash
uv run litestar --app docs.examples.htmx_websocket.app:app run
```

```python
--8<-- "docs/examples/htmx_websocket/app.py"
```

## Application error responses { #error-handling }

An application returns structured responses for its handled validation cases. The intentional raise action remains an uncaught server error; documentation does not install exception handling.

```bash
uv run litestar --app docs.examples.error_handling.app:app run
```

```python
--8<-- "docs/examples/error_handling/app.py"
```

## Broker traits, security and replies { #broker-contracts }

Explicit broker contracts without a transport implementation. The documentation is served at `/asyncapi/`, and the headless export command writes the same document.

```bash
uv run litestar --app docs.examples.contracts:app run
```

```python
--8<-- "docs/examples/contracts.py"
```

## Native schema plugin { #native-schema }

A native Litestar plugin and encoder define a custom Ticket value even with OpenAPI disabled.

```bash
uv run litestar --app docs.examples.native_schema:app run
```

```python
--8<-- "docs/examples/native_schema.py"
```

## Mounted and guarded docs { #mounted-docs }

Native Router nesting mounts `/service/asyncapi`. Send `Authorization: demo-token` to access UI, assets and schema; replace the demonstration guard in production.

```bash
uv run litestar --app docs.examples.mounted_docs:app run
```

```python
--8<-- "docs/examples/mounted_docs.py"
```

## Custom renderers { #custom-renderers }

Scalar at `/events`, native JSON/YAML downloads, and a separate opt-in React console.

```bash
uv run litestar --app docs.examples.renderers:app run
```

```python
--8<-- "docs/examples/renderers.py"
```

## Headless export

The broker example also supports export without starting a server:

```bash
uv run litestar --app docs.examples.contracts:app asyncapi export --format json
uv run litestar --app docs.examples.contracts:app asyncapi export --format yaml --output /tmp/contracts.yaml
```

Existing output files require `--overwrite`. See [Security, servers and mounted docs](../integrations/security-and-servers.md)
for server resolution, security declarations and the native ASGI mount limitation.
