# Concepts and lifecycle

One application can describe three kinds of realtime routes: WebSocket handlers, HTTP routes that stream Server-Sent Events, and ChannelsPlugin topics. This example has one of each:

```python
--8<-- "docs/examples/transports.py"
```

## The generated channels

```json
--8<-- "docs/_generated/fragments/transports/channels.json"
```

## Directions

AsyncAPI describes the application, not its clients. An operation with `action: receive` means the application receives messages, as the chat listener does with its `data` parameter. `action: send` means the application sends them, as the listener's return value, the event stream and the broker topic do. The console in the documentation UI shows the client's view, so its labels are reversed.

## Channels and operations

A channel key names the entry in the document's `channels` map; the `address` is where messages travel. Discovered routes use their path for both, and a ChannelsPlugin topic uses its name. Each operation in the `operations` map refers to one channel and to messages of that channel. Its key comes from the handler name and action, such as `chat_receive`, and is unique without regard to case. AsyncAPI 3 has no `operationId` field, so the key is the operation's identity.

## Discovery sources

Each discovered channel names its source in the `x-litestar-source` extension and carries a matching binding:

- **websocket**: a WebSocket handler, with a `ws` binding.
- **sse**: an HTTP route that returns `ServerSentEvent`, with an `http` binding and `text/event-stream` messages. A stream has no item type, so the payload stays unconstrained until a decorator declares one.
- **channels**: a ChannelsPlugin route or topic, with an empty `bindings` object. The `orders` topic has no route; `channel_payloads` gives it the `Order` schema.

Channels declared in `AsyncAPIConfig.channels` carry no marker. A declared channel replaces a discovered channel with the same key. Two discovered channels with the same key raise `ImproperlyConfiguredException` and name both routes. Handlers with `include_in_schema=False`, on the handler or a parent layer, are left out.

## Lifecycle

Nothing is generated at startup. The first request for the document, a call to `get_asyncapi_schema(app)` or a CLI export builds it from the finalized routes, with a schema registry of its own and the application's schema plugins and type encoders. The result is cached; `clear_cache()` discards it, and `AsyncAPIConfig(use_cache=False)` rebuilds it on every request. `get_asyncapi()` and `get_asyncapi_schema()` return copies, and `get_asyncapi_json()` returns the cached bytes.

An application accepts one `AsyncAPIPlugin`, and a plugin instance belongs to the first application it serves, even with caching off. A second plugin on the same application raises `ImproperlyConfiguredException`, as does using one plugin with a second application. Create one plugin per application.

## Recap

- Operations describe what the application sends and receives, and each refers to one channel.
- WebSocket routes, Server-Sent Event routes and ChannelsPlugin topics are discovered and marked with `x-litestar-source`.
- Next, [WebSocket handlers](websocket-handlers.md) shows what each kind of handler produces.
