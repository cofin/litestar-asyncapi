# ChannelsPlugin

Generated WebSocket routes (`create_ws_route_handlers=True`) are documented
with their path as channel key. Their operation is `send`: the application
publishes messages to subscribers; incoming frames are discarded by the
generated route. Deduplication uses native handler identity so a user socket at
another address is not hidden.

Each configured topic without a generated fixed-topic route, including every
topic under Litestar's default `create_ws_route_handlers=False`, becomes a
topic-only channel keyed by the topic name. It has the description
"ChannelsPlugin broker topic" and one `send` operation named
`{topic}_send`. These channels describe broker topics, not addresses a client
can connect to; hide them with
`AsyncAPIConfig(include_channels_plugin_topics=False)`.

Topics come only from the names passed to the `ChannelsPlugin` constructor and
are read once when the application starts, so runtime subscriptions never change
the document. `arbitrary_channels_allowed=True` without configured names adds
no topic channels. Such a plugin shares its topic list with runtime
subscriptions, so an `AsyncAPIGenerator` used without `AsyncAPIPlugin`
documents none of its topics. A topic named like another channel key, or configured on two
`ChannelsPlugin` instances, raises `ImproperlyConfiguredException`.

Generated and topic-only messages are untyped by default. Map a topic name to a
payload type with `channel_payloads` to document its schema:

```python
AsyncAPIConfig(channel_payloads={"news": Headline, "orders": Order})
```

The topic's generated route and topic-only channel then use the generated
schema with `contentType: application/json`; generated routes keep
`x-websocket-mode`. A key that names no configured topic raises
`ImproperlyConfiguredException`, whatever the include flags say. When a
`ChannelsPlugin` allows arbitrary channels, an unlisted key instead declares a
topic, which then gets a topic-only channel. The arbitrary-channel route
(`.../{channel_name}`) stays untyped.

Every ChannelsPlugin channel carries `x-litestar-source: channels` and an empty
`bindings` object. The empty object is deliberate: it marks a ChannelsPlugin
channel rather than a native WebSocket handler, even under a `/ws/` prefix.

The example retains an HTTP publishing route and a separate typed echo listener:

```python
--8<-- "docs/examples/channels_plugin/app.py"
```

After starting it, publish with:

```bash
curl -X POST http://localhost:8000/publish/news -H 'Content-Type: application/json' -d '{"message":"hello"}'
```

The generated subscriber's uncertain wire format is documentation-only in the
console. A client can subscribe directly to its generated route. For an external
broker contract use explicit `ChannelDefinition` entries, as in
[Security, servers and mounted docs](security-and-servers.md); declaring one does not implement a broker client.
