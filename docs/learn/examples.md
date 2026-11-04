# Runnable examples

Every application under `docs/examples/` is tested: the suite serves its document, and `make validate-asyncapi` checks it against the official AsyncAPI schemas. Run an example from the repository root after `make install` with the Litestar CLI, for example `uv run litestar --app docs.examples.transports:app run`, then open `http://localhost:8000/asyncapi/`.

Each file starts with a PEP 723 block that lists its dependencies and points at this checkout. Running a file directly only builds the application; the Litestar CLI serves it.

Examples that enable the console serve it at `/asyncapi/playground`. Its validation is advisory: it can send text that does not match the schema, so connect it only to servers you control. The applications leave authorization and message validation to you.

## WebSocket listener { #websocket-listener }

Typed dataclass input and output through a DTO. The application receives the input and sends the returned value.

```python
--8<-- "docs/examples/websocket_listener/app.py"
```

## WebSocket stream { #websocket-stream }

An asynchronous generator sends a JSON event every second until the client disconnects.

```python
--8<-- "docs/examples/websocket_stream/app.py"
```

## Server-Sent Events { #server-sent-events }

An HTTP route streams price updates; the decorator declares their payload.

```python
--8<-- "docs/examples/server_sent_events.py"
```

## Discovery sources { #transports }

A WebSocket listener, a Server-Sent Event route and a typed ChannelsPlugin topic in one application.

```python
--8<-- "docs/examples/transports.py"
```

## Raw socket and multiple messages { #decorator-overrides }

A raw socket accepts two named message types and returns a JSON result. Decorators supply its contract.

```python
--8<-- "docs/examples/decorator_overrides/app.py"
```

## Payload schemas { #payload-schemas }

Fixed-length and variable-length tuples, an optional field and an explicit example.

```python
--8<-- "docs/examples/payload_schemas.py"
```

## Channels and publish endpoint { #channels-plugin }

ChannelsPlugin subscriber routes for `news` and `alerts`, a typed `news` payload and a POST route that publishes to either topic.

```python
--8<-- "docs/examples/channels_plugin/app.py"
```

## HTMX HTML fragments { #htmx-websocket }

An HTMX page at `/` exchanges HTML fragments over a WebSocket. It loads HTMX and Pico CSS from public CDNs. The console does not support its text/HTML messages, so they are documented only.

```python
--8<-- "docs/examples/htmx_websocket/app.py"
```

## Application error responses { #error-handling }

The application answers handled validation cases with structured error messages. Its `error` action raises an exception, which stays an uncaught server error; the plugin installs no exception handling.

```python
--8<-- "docs/examples/error_handling/app.py"
```

## Broker request and reply { #broker-contracts }

Typed broker channels declared without a route or broker client. The request operation names its reply channel and message.

```python
--8<-- "docs/examples/contracts.py"
```

## JWT-protected WebSocket { #secured-orders }

`JWTAuth` protects a WebSocket listener. The document inherits the bearer scheme and a `wss` server from the OpenAPI config, refers to the scheme by name, shares one operation trait between both operations and declares a correlation ID.

```python
--8<-- "docs/examples/secured_orders.py"
```

## Native schema plugin { #native-schema }

A Litestar schema plugin and type encoder describe a custom `Ticket` value with OpenAPI disabled.

```python
--8<-- "docs/examples/native_schema.py"
```

## Mounted and guarded docs { #mounted-docs }

Router nesting mounts the documentation at `/service/asyncapi`. Requests need the header `Authorization: demo-token`; replace this demonstration guard in a real application.

```python
--8<-- "docs/examples/mounted_docs.py"
```

## Custom renderers { #custom-renderers }

Scalar at `/events`, JSON and YAML at custom paths, and the React console as a separate page.

```python
--8<-- "docs/examples/renderers.py"
```

## Headless export

Any example can be exported without starting a server, for example `uv run litestar --app docs.examples.contracts:app asyncapi export`. See [Exporting documents](export.md).
