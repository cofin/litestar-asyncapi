# Research Plan: AsyncAPI Quality Hardening for Litestar

## Purpose and Scope

This research document supports a quality hardening effort for the Litestar AsyncAPI plugin. The goal is to document the work required to improve correctness, compliance, safety, and test coverage without changing the core architecture. The research focuses on the AsyncAPI 3.0 specification, Litestar’s plugin and routing model, and the plugin’s current implementation patterns. It also clarifies the observed behavior of Litestar route registration to ensure discovery logic is correctly scoped.

The scope includes the following areas:

- Channel and operation discovery for WebSocket handlers and ChannelsPlugin.
- Schema generation fidelity for common Python typing patterns.
- Component naming and reference stability.
- Renderer safety and content output behavior.
- Test coverage, gaps, and regression scenarios.

Non-goals include the addition of new messaging protocol bindings, major API changes, or re-architecting the plugin. The effort should align with existing patterns and provide incremental improvements.

## Existing Implementation Context

The current implementation follows Litestar’s InitPluginProtocol pattern. It provides an AsyncAPIPlugin, AsyncAPIConfig, schema generation utilities, and discovery for WebSocket routes plus limited ChannelsPlugin support. The AsyncAPI document structure uses dataclass-based spec objects and a to_schema() serializer. The generator builds a document by iterating over discovered channels, creating operations, and populating components from a schema registry.

Key components and their roles:

- `AsyncAPIPlugin` orchestrates initialization, route registration, and caching. It constructs a docs router based on render plugins. The router exposes JSON/YAML/UI endpoints and a simple 404 handler. This follows standard Litestar plugin conventions and is aligned with the project’s patterns.
- `AsyncAPIGenerator` builds the document: it creates `Info`, sets servers and default content type, discovers channels, builds operations, then populates component schemas from the schema registry. It has helper functions for operation IDs, channel keys, and JSON pointer escaping.
- WebSocket discovery (`extract_websocket_channels`) examines `app.routes`, finds `WebSocketRoute` entries, and derives channel parameters and operations based on handler type. It infers receive/send for listeners and send-only for streams.
- ChannelsPlugin discovery uses internal plugin fields for best-effort enumeration of channels and yields a generic send operation with placeholder message schema.
- Schema generation uses `AsyncAPISchemaGenerator` with plugins for Pydantic, attrs, dataclass, msgspec, and TypedDict. It maps type annotations to JSON Schema-like structures.

Overall, the implementation is cohesive and matches the existing design principles. However, specific gaps exist in correctness and spec alignment, particularly in operation IDs, schema details, component naming, and some output safety concerns.

## Litestar Plugin and Routing Model

Litestar’s plugin system supports InitPluginProtocol where `on_app_init()` receives an AppConfig and can register routes, middleware, and dependencies. This matches the plugin’s current approach of appending a docs router during app initialization. Plugins are invoked in order, and documentation should note ordering expectations.

Routing in Litestar is built around route handlers that can be registered on the app or on routers. Routers can be nested. When a Router is registered onto another Router (or the Litestar app), its routes are expanded and merged into the parent’s route list. This matters for discovery: iterating `app.routes` should surface routes registered via nested routers, because registration flattens routes into the app’s `routes` list.

The key flow:

- The Litestar application subclass extends Router and calls `register()` for each route handler specified in the config.
- Router.register() accepts route handlers, controllers, and routers. If a router is registered, it uses the router’s `route_handler_method_map`, which is built from the router’s own `routes` list.
- The router’s `routes` list is populated by registering route handlers during Router initialization, which includes any nested routers.

This means a nested router’s route handlers are represented in the parent’s `routes` list after registration, so the discovery function that walks `app.routes` should include WebSocket routes defined in nested routers. This reduces the risk of missing channels, although tests should confirm this behavior for nested router usage and avoid regressions if Litestar’s internal behavior changes.

## AsyncAPI 3.0 Specification Highlights

The AsyncAPI 3.0 specification is the authoritative reference for document structure and object semantics. Several areas are directly relevant to the plugin’s current implementation and to the required quality work.

### Default Content Type

The AsyncAPI document has a `defaultContentType` that should be applied when a message does not define a `contentType`. The current generator sets this from configuration. The spec emphasizes this as a default that parsers should use when contentType is omitted. It is important to ensure message contentType overrides are respected, and when absent, the default applies. This affects message inference in WebSocket discovery and the schema generator’s handling of content types.

### Channels and Addresses

Channels represent communication endpoints. Each channel can include an address string and optional parameters. The spec allows address expressions with parameters embedded in braces. The channel parameters object describes parameters used in the address. Parameters can be reused and referenced via components, especially when multiple channels share parameter definitions.

Channel parameters are not just metadata: they are the formal place where address parameters are defined in AsyncAPI. The docs emphasize using `parameters` to define each parameter, and optionally defining reusable parameters in `components.parameters`. This has implications for how the plugin models path parameters for WebSocket routes. The current implementation in `extract_websocket_channels()` converts Litestar path parameters to AsyncAPI parameters with a schema and `location="path"`. That is a good start, but it does not use `components.parameters` nor does it enforce the specification’s constraints on allowed schema properties for parameters.

### Operation Objects

Operations represent the actions an application performs on a channel (send/receive). In AsyncAPI v3, the **operations object is a map whose keys are the operationId values**, and the value is an Operation Object. This makes operation IDs structurally unique because object keys must be unique. The Operation Object itself does not need an explicit `operationId` field when it is already expressed as the key. This has implications for the plugin, which currently models `operation_id` as a field and also uses operationId-like keys in the operations map. The document structure should align with the spec’s map-key semantics, or the `operation_id` field should be treated as a compatibility extension if retained.

The specification requires operations to reference a channel and optionally list messages. The `messages` field should be a list of references to messages defined in the channel. In the current implementation, `Operation.messages` uses a list of Message or Reference objects and attaches a concrete Message object derived from discovery. This is not aligned with the current spec language that expects references to channel messages. The spec encourages parsers to dereference for convenience, but the raw document should be aligned with the required structure.

Uniqueness of operation IDs is thus inherent in the operations map, but tooling also relies on the operationId string for stable identifiers. The current generator only de-duplicates the internal map key, not the operationId value embedded in the Operation object, which can lead to duplicate operationId values across operations. This should be treated as a quality issue because it affects downstream tooling and breaks the map-key uniqueness assumption when the key and embedded value diverge.

### Message Objects and Traits

Messages can include payload, headers, contentType, correlationId, traits, and examples. The spec defines Message Trait Objects that can include many fields, which must be merged using JSON Merge Patch and should not override existing fields. The plugin currently supports traits by mapping trait names to component references and attaching those references to message objects, which is a sound approach. However, it does not implement trait merging, and it may attach a message object directly instead of a reference where the spec indicates references are expected. The approach may still be acceptable for internal uses, but there is room to align with spec expectations for message references, trait composition, and contentType defaults.

### Channel Parameters and AsyncAPI v3 Changes

AsyncAPI v3 simplified parameter schemas compared to v2. Parameters now accept a limited set of fields like enum, default, examples, description, and location. The previous version allowed more schema-like validation options. This has implications for Litestar path parameters: the plugin currently uses a Schema object for parameters, which may include more than what v3 allows. This could lead to technically invalid documents if strict validation is applied. The plugin should either constrain parameter schema output to the allowed subset or use a dedicated parameter schema type aligned with v3 rules.

### Dynamic Channel Addresses

AsyncAPI provides explicit guidance on how to express parameters in channel addresses. This is particularly relevant for WebSocket route paths and ChannelsPlugin’s dynamic channel naming. The plugin should ensure that any dynamic address values are properly represented using braces and parameters, and that the parameters object includes matching entries.

## Specific Implementation Risks and Gaps

This section maps specification expectations and Litestar behavior to the current implementation and identifies gaps that need to be addressed in the hardening work.

### 1) Operation ID Uniqueness for ChannelsPlugin

ChannelsPlugin discovery builds a single send operation with a fixed operation_id (e.g., "channels_send") and applies it to each discovered channel. When multiple channels exist, the generator de-duplicates operation keys but does not adjust the operationId itself. This can create multiple operations with the same operationId value. The result is ambiguous in codegen, and it undermines the expectation that operationId can serve as a stable identifier. A fix requires either generating per-channel operationId values or applying a deterministic suffix.

### 2) Channel Parameters Modeling

The plugin uses a `Parameter` model with a `schema` field and a `location` field. This is compatible with prior versions of AsyncAPI and OpenAPI, but AsyncAPI 3.0 reduces the allowed parameter structure. The plugin may need to restrict parameter output to the allowed subset or document that it is a relaxed model. If strict compliance is desired, this should be addressed with a dedicated schema shape for parameters or a conversion layer.

### 3) Schema Generation Fidelity

Schema generation currently handles common builtins, unions, lists, dicts, enums, and a set of model types (Pydantic, attrs, dataclass, msgspec, TypedDict). It does not incorporate detailed constraints (min/max, regex, bounds, length) even when `FieldDefinition` carries them. This can lead to a mismatch between runtime validation and documentation. Additionally, tuple handling is simplified to the first element’s schema; this is incorrect for fixed-length tuples and variadic tuples. Fixing this is important for accurate payload schemas and for differentiating between arrays and tuple-like shapes.

### 4) Component Key Normalization

SchemaRegistry allows a schema component key override, but it does not normalize or sanitize the provided override. If a user supplies a key containing invalid characters, it will be used directly in the component name and reference. This can lead to invalid JSON Pointer paths or noncompliant component names. This should be sanitized or validated, and errors should be surfaced if invalid overrides are detected.

### 5) Renderer Safety

The UI renderer interpolates the AsyncAPI `info.title` into HTML without escaping. While `info.title` typically comes from config, it could be user-controlled in some environments or set from a dynamic source. This creates a potential HTML injection vector. The renderer should escape or sanitize the title to avoid accidentally producing unsafe HTML. This is a low-severity but easy-to-fix issue.

### 6) Operation Messages Structure

The spec indicates operations should reference messages defined in the channel, using a list of message references. The plugin currently attaches a list containing a Message object directly. This divergence may be acceptable for internal tooling, but it diverges from strict spec structure and could create issues with strict validators. A fix would involve populating channel messages with identifiers and then referencing them from operations. This is a broader change and may be treated as part of a larger compliance workstream.

## Testing and Quality Considerations

The test suite covers core functionality including plugin creation, route discovery, and schema generation for several model types. However, there are gaps relevant to the identified issues:

- No tests assert unique operationId values across channels.
- No tests cover nested routers to confirm discovery behavior for WebSocket routes.
- No tests cover tuple schema generation or explicit constraint propagation.
- No tests validate parameter output constraints for AsyncAPI v3.
- No tests cover component key override sanitization.
- No tests cover UI title escaping or output safety.

A quality hardening effort should add tests that target each of these behaviors. Tests should follow the existing function-based pytest pattern and use `pytest.mark.anyio` for async contexts. Coverage should be prioritized for discovery and schema generation modules since they are central to compliance and correctness.

## Dependencies and External Reference Summary

Primary external references for this effort include:

- AsyncAPI 3.0 specification and related concept guides.
- Litestar documentation on plugin usage and route registration.

These references establish the expected behavior for AsyncAPI document structure, channel parameter modeling, and plugin lifecycle integration. They also contextualize how Litestar routing and plugin mechanisms are expected to behave, which informs discovery and caching logic.

## Research Conclusions

The current AsyncAPI plugin implementation is coherent and feature-complete for initial usage, but several correctness and compliance issues should be addressed to improve quality. The most impactful issues are operationId uniqueness for ChannelsPlugin-generated operations and schema generation fidelity for tuples and constraints. Secondary issues include parameter schema compliance with AsyncAPI v3, component key sanitization, and renderer safety.

Litestar’s routing behavior confirms that app.routes includes routes from nested routers after registration. This indicates that discovery logic based on `app.routes` is sufficient for nested routers, though tests should validate this to guard against future changes.

The research supports a multi-task hardening effort that focuses on correctness, compliance, and test coverage without introducing new architecture. The next step is to translate these conclusions into a PRD that documents acceptance criteria, technical approach, file changes, and a comprehensive test plan.

## Sources

- AsyncAPI 3.0 Specification: https://www.asyncapi.com/docs/reference/specification/v3.0.0
- AsyncAPI Document Structure: https://www.asyncapi.com/docs/concepts/asyncapi-document/structure
- AsyncAPI Dynamic Channel Address Parameters: https://www.asyncapi.com/docs/concepts/asyncapi-document/dynamic-channel-address
- AsyncAPI v3 Migration Notes (Parameters): https://www.asyncapi.com/docs/migration/migrating-to-v3
- Litestar Plugins Docs: https://docs.litestar.dev/2/usage/plugins/index
- Litestar Routing Docs: https://docs.litestar.dev/2/usage/routing/index
