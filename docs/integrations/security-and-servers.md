# Security, servers and mounted docs

This application describes a broker it talks to through explicit contracts: a server, a security scheme, reusable traits, and an operation that expects a reply. It has no routes and creates no broker client:

```python
--8<-- "docs/examples/contracts.py"
```

## The generated contract

```json
--8<-- "docs/_generated/fragments/contracts/servers.json"
```

```json
--8<-- "docs/_generated/fragments/contracts/components-securitySchemes.json"
```

```json
--8<-- "docs/_generated/fragments/contracts/channels.json"
```

## Servers

A `Server` splits a connection URL into `protocol` (such as `ws`, `wss` or `amqp`), `host` with an optional port, and `pathname` for a deployment prefix. A channel `address` is resolved below that prefix: `host="localhost:8000"`, `pathname="/service"` and `address="/events"` give `ws://localhost:8000/service/events`. Give the prefix once, on the server. Servers appear only when configured; the request's host name never becomes one.

## Security schemes

Put security schemes in `Components(security_schemes=...)` and refer to them from servers and operations with `Reference("#/components/securitySchemes/<name>")`, as `acceptOrder` does. A scheme documents a requirement; it installs no authentication. An API key in the query string uses `type="httpApiKey"` with `in_="query"`. Browser WebSockets cannot send arbitrary headers, and the plugin provides no proxy for them.

## Explicit broker, traits and replies

`ChannelDefinition` declares a channel that no route provides. Its `key` names the channel in the document and its `address` is the broker destination. Operations and messages take the same definitions as the decorators. Traits listed by name in an operation or message must be registered in `operation_traits` or `message_traits`.

A reply names its channel and messages by reference, and those messages must belong to the reply channel. Local references are checked against the places AsyncAPI allows them; external references are kept as written and never fetched. Configured components cannot replace a schema that the application generates under the same name.

## Guarded, mounted documentation

Litestar guards in `DocsConfig.guards` protect every documentation route: the UI, JSON, YAML, console and assets. They do not protect the sockets that the document describes. To mount the documentation under a router, turn off the automatic mount and register the plugin's router yourself:

```python
--8<-- "docs/examples/mounted_docs.py"
```

The documentation is now at `/service/asyncapi/`, and requests need the header `Authorization: demo-token`; the token check is a demonstration, not an authentication scheme. Links include router prefixes and a correctly set ASGI `root_path`, so `root_path="/gateway"` adds that prefix. Litestar 2.24 does not add a prefix of its own when the application is mounted as an arbitrary ASGI app, so such a mount must pass the full `root_path` in the scope; the plugin does not rebuild URLs from `raw_path`.

## Headless export

Export works without documentation routes, so it also suits applications that use `DocsConfig(enabled=False)`. See [Exporting documents](../learn/export.md).
