# WebSocket handlers

A WebSocket stream sends every value its generator yields:

```python
--8<-- "docs/examples/websocket_stream/app.py"
```

## The generated channel

```json
--8<-- "docs/_generated/fragments/websocket_stream/channels.json"
```

## Streams

A stream only sends, so its channel has one `send` message and one `send` operation. The yielded type, `StreamItem`, becomes the payload schema. Litestar sends strings as text frames, bytes as binary frames and other values as JSON text, and the document records that frame type in the `x-websocket-mode` extension, separate from the logical `contentType`. `x-websocket-mode` is an extension of this library, not a field of the standard WebSocket binding.

## Listeners

A listener, as in the [installation example](installation.md), has both directions. The annotation of its `data` parameter describes the messages the application receives, and its return annotation describes the messages it sends. With a DTO, the schema describes the shape the DTO transfers rather than the model itself.

## Raw sockets

A handler declared with `@websocket` reads and writes frames itself, so its parameters say nothing about the messages. Undecorated raw handlers are left out of the document. Describe them with the [decorators](decorators.md), or set `AsyncAPIConfig(include_raw_websocket_routes=True)` to document them with unconstrained payloads and a warning.

## Handler metadata

A handler's own `summary`, `description` and `operation_id` fill the operation fields that decorators leave empty. With `AsyncAPIConfig(use_handler_docstrings=True)`, the handler's docstring fills the description too. This also applies to operations that a decorator adds, such as the explicit operations of a raw socket.

`include_in_schema=False` on a handler, router or controller removes its routes from the document. Messages that reach the application through a broker rather than a route are not inferred; declare them as [explicit channels](../integrations/security-and-servers.md#explicit-broker-traits-and-replies).

## Server-Sent Events

An HTTP route that returns `ServerSentEvent` streams events to the client, so it becomes a channel with one `send` operation:

```python
--8<-- "docs/examples/server_sent_events.py"
```

```json
--8<-- "docs/_generated/fragments/server_sent_events/channels.json"
```

`ServerSentEvent` does not record what its iterator yields, so the payload comes from the `asyncapi_message` decorator; without one, the payload is unconstrained. Messages use `contentType: text/event-stream`, the channel carries an `http` binding and `x-litestar-source: sse`, and path parameters become channel parameters.

Only the AsyncAPI decorators describe these channels. The handler's HTTP `summary`, `description` and `operation_id` belong to the OpenAPI document. Declaring a `receive` operation on a Server-Sent Event route raises `ImproperlyConfiguredException`.

The channel key is the route path. When a WebSocket route uses the same path, the key becomes `{path}:sse`; when several HTTP methods stream from one path, each gets `{path}:sse:{method}`. The address stays the path. `AsyncAPIConfig(include_sse_routes=False)` turns this discovery off.

## Recap

- Streams send, listeners receive and send, and raw sockets need explicit metadata.
- HTTP routes that return `ServerSentEvent` become send-only channels marked `x-litestar-source: sse`.
- Next, [Decorators](decorators.md) shows how to declare operations and messages explicitly.
