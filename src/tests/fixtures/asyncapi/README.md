# AsyncAPI conformance fixtures

Run `npm ci` with Node (`.nvmrc`), then `make validate-asyncapi`. Node packages are development-only. To validate independent exports, pass local JSON paths to `npm run validate:asyncapi -- path/to/document.json`. `make validate-asyncapi` also exports `tests.fixtures.apps.cli:app` through the CLI and validates the result. The `websocket-*` and `boolean-*` fixtures remain independent hand-written contracts. The `bindings-*` fixtures are generated from `tests.fixtures.apps.bindings` by the same export path; they cover Kafka and AMQP bindings and `x-` extensions on servers, messages, traits and component channels and operations, and `make test` fails if they drift from a fresh export. The `realtime-*` fixtures are generated the same way from `tests.fixtures.apps.realtime`; they cover the `x-litestar-source` transport marker and channel bindings of discovered WebSocket, Server-Sent Event, ChannelsPlugin route and ChannelsPlugin topic-only channels next to an explicit channel.

The gate applies both the pinned `@asyncapi/specs` 6.11.1 document schema and `@asyncapi/parser` 3.6.3. Parser errors fail validation and the parser must return a document. Warnings do not fail validation. AJV 8.20.0 validates Draft07 payload instances separately: tuple ordering, missing elements and extra elements are checked explicitly. Document validation alone does not establish payload-instance validity.

The valid corpus covers 3.0.0 and 3.1.0, WebSocket bindings and parameters, multiple messages, traits, security, replies and null examples. Invalid mutations are created in memory, never stored among the valid documents. Tests require rejection of operationId, dangling references, operation-message membership violations, malformed example objects and external references. Only fragment references are accepted; HTTP, file and relative external references are rejected before the parser runs. Dependency installation needs network access; validation does not.

## Known official-schema discrepancy

Both pinned official document schemas reject a direct `payload: false`. The `anySchema` conditional uses `required: [schema]` without an object type guard, so a boolean takes the branch expecting an object-shaped MultiFormatSchema. This is an upstream schema discrepancy, not evidence that boolean JSON Schemas are semantically invalid.

The valid boolean fixtures use an explicit `application/schema+json;version=draft-07` MultiFormatSchema containing `schema: false`. A separate generated diagnostic mutation verifies the official rejection of direct booleans. It neither weakens the conformance gate nor submits an upstream report.

## Parser literal-reference limitation

Spectral's generic resolver interprets `$ref` even inside example/default/const/enum data. The gate validates the original document unchanged with the official schema, then gives the parser a disposable copy that hides `$ref` data keys inside literal fields and extensions. Named maps remain reference-aware, including channels named `examples` and schema properties named `default`. Valid examples include nested HTTP/file-looking `$ref` literals. This parser workaround does not validate literal payload contents; separate Draft07 instance assertions establish tuple semantics.

A second isolated diagnostic covers a valid schema property literally named `$ref`: `properties: {"$ref": {"type": "string"}}`. Official schema validation accepts it, but parser 3.6.3's circular-reference normalization unconditionally treats the object-valued map entry as a reference and throws `path.startsWith is not a function`. The gate preserves this upstream diagnostic separately; it does not rename properties or admit parser failures into the valid corpus.
