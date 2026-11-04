# Security, servers and mounted docs

This application protects a WebSocket route with Litestar's `JWTAuth`. The document takes its title, the bearer scheme that `JWTAuth` registers and a `wss` server from the application's OpenAPI config:

```python
--8<-- "docs/examples/secured_orders.py"
```

## The generated contract

```json
--8<-- "docs/_generated/fragments/secured_orders/servers.json"
```

```json
--8<-- "docs/_generated/fragments/secured_orders/components-securitySchemes.json"
```

```json
--8<-- "docs/_generated/fragments/secured_orders/operations.json"
```

## Inherited from OpenAPI

The plugin reads `app.openapi_config` when it builds the document, after auth backends such as `JWTAuth` have added their components. It never changes that config.

- **Metadata.** Unset `title`, `version`, `description`, `contact`, `license`, `terms_of_service` and `external_docs` on `AsyncAPIConfig` come from the OpenAPI config, and explicit values win. Tags group HTTP routes, so they are not inherited. OpenAPI's `summary` and the license `identifier` have no AsyncAPI equivalent.
- **Security schemes.** Scheme definitions are added to `components.securitySchemes` under their OpenAPI names. Security requirements are not inherited, because AsyncAPI cannot express OpenAPI's alternatives, optional authentication or excluded routes.
- **Servers.** Only with `inherit_openapi_servers=True`; see [Servers](#servers).

`AsyncAPIConfig(inherit_openapi=False)` turns all of this off.

Schemes are converted as follows. A scheme or OAuth flow that AsyncAPI cannot express is skipped with a warning.

| OpenAPI | AsyncAPI |
| --- | --- |
| `http` with `bearer` | `http` with `scheme: bearer` and `bearerFormat`; the header `name` is dropped |
| `http` with another scheme, such as `basic` | `http` with that scheme in lowercase |
| `apiKey` in a header, query or cookie | `httpApiKey` |
| `oauth2` | `oauth2`; each flow keeps its URLs and gets `availableScopes`; flows with relative URLs are skipped |
| `openIdConnect` | `openIdConnect` |
| `mutualTLS` | `X509` |

A scheme in `AsyncAPIConfig.components` with the same name as an inherited one must convert to the same definition; otherwise building the document raises an error naming both.

## Servers

A `Server` splits a connection URL into `protocol` (such as `ws`, `wss` or `amqp`), `host` with an optional port, and `pathname` for a deployment prefix. A channel `address` is resolved below that prefix: `host="localhost:8000"`, `pathname="/service"` and `address="/events"` give `ws://localhost:8000/service/events`. Give the prefix once, on the server. Servers appear only when configured or derived from OpenAPI; the request's host name never becomes one.

`AsyncAPIConfig(inherit_openapi_servers=True)` derives servers from the application's `OpenAPIConfig.servers`. Absolute `http` URLs become `ws` servers and `https` URLs `wss` servers, keeping the path, description and variables. Relative URLs, including Litestar's default `/`, are skipped. The derived servers are named `openapi`, `openapi_2`, and so on, and only channels discovered from WebSocket routes list them, because a channel without `servers` belongs to every server. It is off by default because WebSocket routes may be served from another host.

When derived servers are present, SSE, ChannelsPlugin and explicit channels must each declare a nonempty `ChannelDefinition.servers` list. Building the document raises a configuration error otherwise: an omitted or empty list would advertise those channels on every derived WebSocket server too. Declare the full explicit contracts in `AsyncAPIConfig.channels`, including each channel's operations and messages, because an explicit definition replaces discovery. Set `include_channels_plugin_topics=False` when supplying explicit broker-topic contracts.

## Security schemes

Operations name the schemes they need, as `security=["BearerToken"]` does above. A name can refer to an inherited scheme or to one in `Components(security_schemes=...)`; an unknown name raises an error that lists the valid names. Scheme objects and `Reference`s are also accepted. In the same way, `ChannelDefinition(servers=["broker"])` names the servers that host a channel.

A scheme documents a requirement; it installs no authentication. An API key in the query string uses `type="httpApiKey"` with `in_="query"`. Browser WebSockets cannot send arbitrary headers, and the plugin provides no proxy for them.

## Traits and correlation IDs

`operation_traits` registers reusable operation fields under `components.operationTraits`, and operations list them by name; here both operations share the `orders` tag through one trait. Message traits work the same way through `message_traits`. A `CorrelationId` gives the runtime expression that pairs a request with its response, such as `$message.payload#/order_id`.

Local references are checked against the places AsyncAPI allows them; external references are kept as written and never fetched. Configured components cannot replace a schema that the application generates under the same name. For broker channels without a route and replies, see [Contracts without a route](../learn/decorators.md#contracts-without-a-route).

## Guarded, mounted documentation

Litestar guards in `DocsConfig.guards` protect every documentation route: the UI, JSON, YAML, console and assets. They do not protect the sockets that the document describes. To mount the documentation under a router, turn off the automatic mount and register the plugin's router yourself:

```python
--8<-- "docs/examples/mounted_docs.py"
```

The documentation is now at `/service/asyncapi/`, and requests need the header `Authorization: demo-token`; the token check is a demonstration, not an authentication scheme. Links include router prefixes and a correctly set ASGI `root_path`, so `root_path="/gateway"` adds that prefix. Litestar 2.24 does not add a prefix of its own when the application is mounted as an arbitrary ASGI app, so such a mount must pass the full `root_path` in the scope; the plugin does not rebuild URLs from `raw_path`.

## Headless export

Export works without documentation routes, so it also suits applications that use `DocsConfig(enabled=False)`. See [Exporting documents](../learn/export.md).
