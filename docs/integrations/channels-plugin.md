# ChannelsPlugin

This application lets `ChannelsPlugin` create subscriber routes for two topics, gives the `news` topic a payload type and adds a route that publishes to either topic:

```python
--8<-- "docs/examples/channels_plugin/app.py"
```

Start it and publish a message:

```bash
uv run litestar --app docs.examples.channels_plugin.app:app run
curl -X POST http://localhost:8000/publish/news -H 'Content-Type: application/json' -d '{"message":"hello"}'
```

## The generated channels

```json
--8<-- "docs/_generated/fragments/channels_plugin/channels.json"
```

## Generated subscriber routes

With `create_ws_route_handlers=True`, `ChannelsPlugin` adds a WebSocket route per topic. Each one becomes a channel keyed by its path with a single `send` operation: the application publishes to subscribers, and the route discards incoming frames. The echo listener at `/ws/echo` is a separate handler and is documented as one.

## Topic payloads

Topic messages are untyped unless `channel_payloads` maps the topic name to a type. Here `news` refers to the generated `PublishPayload` schema with `contentType: application/json`, while `alerts` keeps an unconstrained payload. Generated routes keep their `x-websocket-mode`.

A key in `channel_payloads` must name a configured topic, or `ImproperlyConfiguredException` is raised, even when ChannelsPlugin discovery is turned off. When a `ChannelsPlugin` allows arbitrary channels, an unlisted key instead declares a new topic. The arbitrary-channel route, whose path ends in `{channel_name}`, stays untyped.

## Topic-only channels

A topic without a generated route, which includes every topic under Litestar's default `create_ws_route_handlers=False`, becomes a channel keyed by the topic name. It has the description "ChannelsPlugin broker topic" and one `send` operation named `{topic}_send`. It describes a broker topic, not an address a client can connect to. The [concepts example](../learn/concepts.md) shows one. Turn these channels off with `AsyncAPIConfig(include_channels_plugin_topics=False)`, or all ChannelsPlugin discovery with `include_channels_plugin=False`.

Topics come from the names passed to the `ChannelsPlugin` constructor, read once at startup, so runtime subscriptions never change the document. A plugin with `arbitrary_channels_allowed=True` and no configured names adds no topic channels. A topic named like another channel key, or configured on two `ChannelsPlugin` instances, raises `ImproperlyConfiguredException`. An `AsyncAPIGenerator` used without `AsyncAPIPlugin` documents no topics of a plugin that allows arbitrary channels, because only the plugin records the configured names at startup.

## Markers

Every ChannelsPlugin channel carries `x-litestar-source: channels` and an empty `bindings` object. The empty bindings tell it apart from a native WebSocket handler, even when both live under the same path prefix.

Clients subscribe to the generated routes directly. For a broker that the application reaches without ChannelsPlugin, declare [explicit channels](security-and-servers.md#explicit-broker-traits-and-replies); declaring them does not create a broker client.
