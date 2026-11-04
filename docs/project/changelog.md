# Changelog

All notable changes to this project will be documented in this file.


## 0.3.0

This release fixes generated contracts and the published import, inherits document metadata and security schemes from Litestar's OpenAPI config, and documents Server-Sent Event routes and ChannelsPlugin topics. It requires Python 3.11 and includes breaking changes to operation keys, Kafka binding keys and the default document title. See the [migration guide](migration.md).

### Changed

- Python 3.10 is no longer supported. The package requires Python 3.11 or newer
  and is tested on Python 3.11 to 3.15.
- The AsyncAPI enums (`OperationAction`, `SchemaType`, `SchemaFormat`,
  `SecuritySchemeType`) are `StrEnum`s, so `str()` returns the wire value.
- The document title now defaults to the application's OpenAPI title, which is
  `Litestar API` unless you set one, instead of `AsyncAPI`. This is a breaking
  change; set `AsyncAPIConfig(title=...)` to keep a fixed title.

### Added

- Document metadata is inherited from the application's `OpenAPIConfig`.
  Unset `title`, `version`, `description`, `contact`, `license`,
  `terms_of_service` and `external_docs` on `AsyncAPIConfig` are filled from
  it, and explicit values win. Tags are not inherited. Turn this off with
  `AsyncAPIConfig(inherit_openapi=False)`.
- Security schemes defined in the application's OpenAPI config, including the
  ones Litestar auth backends such as `JWTAuth` register, are added to
  `components.securitySchemes`. Bearer, other HTTP, API key, OAuth2, OpenID
  Connect and mutual TLS schemes are converted to their AsyncAPI form. Schemes
  and OAuth flows that AsyncAPI cannot express, such as flows with relative
  URLs, are skipped with a warning. Security requirements are not inherited, and
  a configured scheme with the same name but a different definition raises.
- `AsyncAPIConfig(inherit_openapi_servers=True)` turns absolute OpenAPI server
  URLs into `ws` and `wss` servers, with their path, description and
  variables. Only channels discovered from WebSocket routes are bound to them.
  Relative URLs are skipped. Other channels require explicit nonempty server
  lists when derived servers exist; an omitted or empty list would select every
  document server. It is off by default.
- Contracts can refer to things by name instead of JSON pointer.
  `OperationDefinition.security` takes scheme names such as `["BearerToken"]`,
  `ChannelDefinition.servers` takes server names, and the new
  `ReplyDefinition(channel, messages, address)` names the reply channel and its
  messages. Unknown names raise with the valid names listed, and a reply message
  must belong to the reply channel. A bare string in place of a list raises
  `TypeError`. Objects and `Reference`s keep working.
- Every discovered channel now says which transport it uses. A channel carries
  `x-litestar-source` set to `websocket` or `channels`, and an explicit
  `bindings` object: native WebSocket channels get a `ws` binding and
  ChannelsPlugin channels get an empty one. Client generators can pick the right
  client from the document alone.
- HTTP routes that return `ServerSentEvent` are discovered as send-only
  channels with `contentType: text/event-stream`, an `http` binding and
  `x-litestar-source: sse`. Type their payload with `asyncapi_message`, and
  turn discovery off with `AsyncAPIConfig(include_sse_routes=False)`.
- Topics configured on a `ChannelsPlugin` are documented even without
  generated WebSocket routes, which is Litestar's default. Each topic without a
  route becomes a channel keyed by its name with one `send` operation. Topics
  are read when the application starts, so runtime subscriptions never appear.
  Turn this off with `AsyncAPIConfig(include_channels_plugin_topics=False)`.
- `AsyncAPIConfig.channel_payloads` maps a ChannelsPlugin topic name to a
  payload type. The topic's generated route and topic channel then document the
  generated schema as `application/json`. Unknown topic names raise unless a
  plugin allows arbitrary channels, in which case the name declares a topic.
- `ChannelDefinition` accepts `description` and `extensions`. Explicit
  channels get no automatic transport marker.

### Fixed

- The package imports again with only `litestar` installed. Pydantic is needed
  only when `create_examples=True`.
- Kafka binding keys now use their official names: `schemaRegistryUrl` and
  `schemaRegistryVendor` on servers, and `schemaIdLocation`,
  `schemaIdPayloadEncoding` and `schemaLookupStrategy` on messages.
  Documents using these bindings now pass official validation. This is a
  breaking change for anyone matching the old `registry_*`, `id_*` or
  `lookup_strategy` keys.
- An explicit `Schema(prefix_items=...)` now exports Draft07 tuple items: the
  positional schemas become an `items` array and `items` becomes
  `additionalItems`. Previously the Draft07 document carried `prefixItems`,
  which validators ignore. Setting `items`, `additional_items` and
  `prefix_items` together now raises `ValueError`.
- A variable-length tuple with length limits, such as
  `Annotated[tuple[int, ...], Parameter(max_items=3)]`, now keeps its item
  type. Previously its items were exported as `oneOf` an integer or anything.
- Length limits of zero (`min_items`, `max_items`, `min_length`,
  `max_length`) are no longer dropped from payload schemas.
- An optional payload such as `Payload | None` now uses the examples declared
  on `Payload` instead of a randomly generated one.
- A payload given as a type name resolved through the application's
  `signature_namespace` now gets a generated example. Previously the example
  was omitted with an "Unsupported type" warning.
- A `None` default on an optional field such as `int | None = None` is now
  exported only on the field itself. Its non-null members, including shared
  enum components, no longer carry a contradictory `default: null`.
- Payload schema errors are easier to read: they carry a single `500:`
  prefix, show the payload type by name instead of its full field definition,
  and a failing component names only the payloads that use it.
- `websocket_listener` operations and their inferred messages are now named
  after the handler function, for example `chat_receive` and `chat_send`.
  Previously every listener was named `ListenerHandler_receive` or
  `ListenerHandler_send`, numbered `_2`, `_3` in route order, so
  `strict_uniqueness=True` failed on any app with two listeners. This is a
  breaking change for anyone matching the old operation or message keys.
- Operations added by `asyncapi_operation` or `asyncapi_message` now get the
  handler's `summary`, `description`, `operation_id` and docstring when the
  decorator sets none. Decorator values still win.
- `asyncapi_operation(messages=...)` and `asyncapi_message` now merge their
  messages in either stacking order. Previously `messages=` silently dropped
  messages added by `asyncapi_message` placed below it. Declaring the same
  message name twice now raises `ValueError` instead of keeping only the last
  declaration.
- `OperationDefinition` now accepts an action in any case or with surrounding
  spaces, such as `" Send "`, as the decorators already did. Previously it
  raised `ValueError`.
- `AsyncAPIConfig` now rejects an unsupported `spec_version` such as
  `"3.0"` with `ValueError`. Previously the value was written into the
  document unchecked.
- Registering a second `AsyncAPIPlugin` on one application now raises
  `ImproperlyConfiguredException` at startup, naming both docs paths.
  Previously both docs sites shared fixed route names, so one docs page could
  link to the other's document and assets, including a guarded one. Use one
  plugin per application.
- `DocsConfig` now rejects a `path` at the application root, such as
  `"/"` or `""`, with `ValueError`. Previously the docs fallback route
  became the application's 404 page and the docs guards applied to every
  unmatched request.
- The interactive console now opens for payloads typed `[object, null]` and
  for `oneOf` or `anyOf` unions whose members are all objects or arrays.
  Previously these operations showed "Interactive sending is unavailable".

## 0.2.0

This release redesigns the plugin around native Litestar components and packaged upstream rendering. See the [migration guide](migration.md) for imports, configuration mappings and wire changes.

- Default to AsyncAPI 3.1, retain explicit 3.0, and correct Draft07 tuple output,
  examples, security references, null preservation and operation map keys.
- Reuse native Litestar schema generation, DTOs, encoders, routing, CLI and
  JSON/YAML render plugins. Remove the duplicate schema engine and unused shims.
- Discover finalized routes, preserve application-relative directions, and add
  typed explicit contracts with multiple messages, traits, replies and provenance.
- Bind cached documents to one application and return defensive public copies.
- Package AsyncAPI React component 3.2.1 with React 18.3.1 and optional Scalar
  1.69.2. Scalar remains opt-in due to demonstrated schema-display gaps.
- Replace the bespoke playground with optional upstream asyncapi-ws-plugin 0.1.0
  interaction. Validation is advisory; intentionally invalid input can be sent.
- Relocate UI sources and frontend tests to `tools/frontend/`, keeping the repository root clean.
- Isolate Playwright output artifacts into `.tmp/test-results`.
- Uncap the Litestar version constraint to `litestar>=2.24.0` without a major-version ceiling.
- Add headless JSON/YAML export and installed-wheel validation across Python
  3.10–3.14 with Litestar 2.24 as the supported minimum.

## 0.1.0

- Initial release with AsyncAPI support for Litestar applications.
