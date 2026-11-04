# Decorators

A raw WebSocket handler reads and writes frames itself, so the decorators describe its messages. This one accepts two kinds of incoming message and sends a result:

```python
--8<-- "docs/examples/decorator_overrides/app.py"
```

## The generated operations

```json
--8<-- "docs/_generated/fragments/decorator_overrides/operations.json"
```

## How it works

Place the AsyncAPI decorators above the Litestar route decorator. They read and update the route handler that the Litestar decorator creates, not the plain function. Every decorator names an `action` from the application's point of view: `receive` for messages the application accepts, `send` for messages it emits.

`asyncapi_operation` declares the whole operation for one action. Its `messages` list offers several named choices, here `Incoming` and `Reset`, each a `MessageDefinition` with its own payload type, content type and examples. `operation_id="incoming_receive"` sets the operation's key in the document; without it, the key comes from the handler or the channel, as for `ws_overrides_send`.

`asyncapi_message` adds one message to the operation for its action, creating the operation when needed. The handler above uses it for the `Result` message it sends. When an operation already has messages, every further message needs a `name`, and messages from both decorators are combined by name in either stacking order. A repeated name raises `ValueError`.

Explicit values win over inference, and an explicit empty list is a value: `messages=[]` documents an operation without messages, and `examples=[]` turns off generated examples for that message. Tags take `Tag` objects rather than strings. To give an example headers, a name or a summary, pass a `MessageExample`; other values become the example's payload, and an explicit `None` payload is kept as `null`.

The same decorators describe [Server-Sent Event routes](websocket-handlers.md#server-sent-events), where only `send` operations are allowed. For contracts that have no route, such as a broker topic consumed elsewhere, use `ChannelDefinition` in `AsyncAPIConfig.channels`; see [Security and servers](../integrations/security-and-servers.md#explicit-broker-traits-and-replies).

## Recap

- Decorators go above the route decorator and always name an action.
- `asyncapi_operation` declares an operation with named message choices; `asyncapi_message` adds one message.
- Next, [Schema generation](schema-generation.md) explains how payload types become schemas.
