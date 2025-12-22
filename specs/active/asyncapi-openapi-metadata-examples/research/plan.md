# Research Plan: OpenAPI Parity for AsyncAPI Metadata, Docstrings, and Examples

## Purpose
This research document collects and synthesizes the information needed to design OpenAPI parity features for the AsyncAPI plugin in litestar-asyncapi. The focus is on aligning the AsyncAPI output with the richer metadata and example behavior that Litestar already provides for OpenAPI, including docstring-driven descriptions and automatically generated examples. The goal is to ground the PRD in current codebase patterns, Litestar configuration capabilities, and the AsyncAPI 3.0 specification requirements.

## Current Plugin Architecture (local codebase)

The plugin is structured around a standard Litestar InitPluginProtocol model, with an AsyncAPIConfig dataclass that provides settings for schema generation, UI routes, and component traits. The schema is built by AsyncAPIGenerator, which performs route discovery via the websocket and channels extractors, then builds AsyncAPI spec objects using dataclasses such as AsyncAPI, Info, Channel, Message, Operation, etc. These objects serialize themselves via BaseSchemaObject.to_schema() and the output is rendered with HTML/JSON/YAML render plugins.

Key pieces that influence metadata and examples today:

- The `AsyncAPIConfig` includes document metadata (title, version, description), default content type, render plugins, and component traits (operation traits and message traits). There are no flags for docstring parsing, example generation, or OpenAPI-like schema generation options. The config is the most likely place to surface parity options since it mirrors the OpenAPIConfig pattern in Litestar.

- The websocket extractor (`_asyncapi/extractors/websocket.py`) derives operations from WebsocketListenerRouteHandler and WebsocketStreamHandler. It creates DiscoveredOperation objects with action, operation_id, summary, description, and traits, but today those values are only set by defaults (operation_id from handler name) or by the AsyncAPI decorators. It does not consult Litestar route handler metadata or docstrings.

- Decorator overrides are stored in `route_handler.opt[ASYNCAPI_OPT_KEY]` with AsyncAPIMetadata, AsyncAPIOperationMetadata, and AsyncAPIMessageMetadata. This is the only current mechanism to set summary/description/title/name per operation or message. There is no parallel to OpenAPI behavior where route handlers can declare summary/description, and docstrings can be used to populate descriptions.

- DiscoveredMessage has fields for payload, summary, description, headers, etc., but no field for examples or example generation. The final Message spec class supports `examples`, yet nothing populates it. Schemas generated for payloads can include default and constraints, but no example values are produced or injected.

- The schema generator (`_asyncapi/schema_generation`) uses FieldDefinition and KwargDefinition (similar to OpenAPI schema generation) to apply constraints like min/max, pattern, numeric bounds, enum, and default. It does not consider example hints, schema titles, or descriptions from FieldDefinition metadata.

- Tests exercise decorator overrides, schema generation, and basic generator behavior, but there are no tests for docstring extraction, example generation, or route metadata adoption. Existing tests show how operations are generated and how unique operation IDs are enforced.

These points establish that the AsyncAPI plugin has the right conceptual hooks, but it lacks the integration points that OpenAPI uses for documentation metadata and example generation.

## Litestar OpenAPI capabilities (documentation and behavior)

Litestar provides a configurable OpenAPI schema generator and a rich OpenAPIConfig. Key documented features relevant to parity include:

- OpenAPI schema generation supports route-level configuration and global config. The docs indicate that users can configure the OpenAPI generation by passing an OpenAPIConfig to Litestar, and can customize the schema in multiple ways.

- OpenAPIConfig has a `create_examples` option. This option can be `False`, a Polyfactory factory, or a mapping of types to factories. When enabled, Litestar generates schema examples automatically. There is also a `random_seed` and `use_handler_docstrings` flag in the OpenAPIConfig signature. Those fields imply that OpenAPI uses a docstring parsing path and example generation logic that could be mirrored.

- OpenAPI spec structures support `examples` on schema objects and request/response bodies, and the Litestar docs highlight that examples can be generated and shown by OpenAPI UI renderers. There are entries in the changelog noting fixes to the OpenAPI examples format and a feature to support `ResponseSpec(..., examples=[...])`.

- Litestar OpenAPI UIs are modular render plugins similar to the AsyncAPI render plugins. OpenAPI provides multiple UI options, but the key for this effort is that OpenAPI uses a plugin-based render system that consumes a rich schema with examples, summary/description, and docstring-driven context.

Based on these doc sections, parity can be defined as: AsyncAPI should accept similar configuration toggles (create_examples, random_seed, use_handler_docstrings), should use route handler metadata when available (summary, description, operation_id), should integrate docstrings into description text, and should attach generated examples to the appropriate AsyncAPI Message or Schema fields.

## AsyncAPI 3.0 spec capabilities

AsyncAPI 3.0 defines operations, messages, and schemas with fields that closely match OpenAPI equivalents. The Message object supports `name`, `title`, `summary`, `description`, `payload`, `headers`, `correlationId`, `contentType`, `tags`, `externalDocs`, `bindings`, `traits`, and `examples`. Schemas are JSON Schema dialect objects with typical keywords, including `examples` and `description`.

This implies that several of the OpenAPI metadata concepts map cleanly into AsyncAPI:

- Operation summary/description map to AsyncAPI Operation summary/description.
- Handler docstrings can be stored as Operation.description or Message.description depending on handler type.
- Example payloads can be stored as Message.examples or Schema.examples. Both are valid in AsyncAPI. The AsyncAPI UI (official AsyncAPI React/Standalone) appears to render message examples under “Payload examples,” so message-level examples are appropriate when available.

Because AsyncAPI allows both message-level examples and schema examples, we need to decide how to prioritize or combine them for parity with OpenAPI behavior. OpenAPI’s `create_examples` typically ends up under the media type examples or schema examples; the AsyncAPI path should be consistent and avoid duplicating conflicting data. The spec also allows contentType overrides and binding-specific metadata, but these are secondary to the parity goal.

## Gap Analysis

1. **Docstring handling**
   - OpenAPI has a documented `use_handler_docstrings` option and presumably extracts docstrings when enabled. AsyncAPI does not expose any such config, nor does it read docstrings.
   - In the current AsyncAPI extractor, the only metadata input is decorators. Litestar handlers themselves can include summary/description in the decorator, but those values are not used in AsyncAPI extraction.
   - Result: AsyncAPI descriptions are sparse unless explicitly annotated via asyncapi_operation/asyncapi_message decorators.

2. **Route handler metadata**
   - OpenAPI consumes handler-level metadata (summary, description, tags, response spec, etc.) that is typically attached by Litestar decorators or by helper functions.
   - AsyncAPI does not currently map these, leaving important context such as route descriptions, tag groupings, or operation IDs unpopulated. Operation IDs are auto-derived but not aligned with any user-specified OpenAPI or handler-specific identifiers.

3. **Examples**
   - OpenAPI supports explicit examples and automatically generated examples. AsyncAPI message object has an examples field but nothing populates it. Schema objects also have an examples field but no pipeline fills it.
   - The Schema generation layer currently handles constraints and defaults only. It does not parse `FieldDefinition` metadata for title/description/example fields.

4. **Testing and documentation**
   - There are no tests verifying docstring extraction, example generation, or metadata mapping.
   - Docs for AsyncAPI do not mention parity with OpenAPI nor how to configure example generation, and sample apps do not show docstring usage.

## Candidate approaches

### Approach A: Lightweight metadata mapping (no example generation)
- Add `use_handler_docstrings` to AsyncAPIConfig and extract docstrings as operation or message descriptions.
- Read metadata from route handler (e.g., summary, description, operation_id) if available.
- Do not implement example generation; rely on user-provided examples via AsyncAPI decorators or message traits.

Pros: Minimal complexity, low risk.
Cons: Does not satisfy the example parity objective; still requires manual annotations.

### Approach B: Metadata mapping + example generation using existing Litestar utilities
- Add `create_examples`, `random_seed`, `use_handler_docstrings` to AsyncAPIConfig with semantics aligned to OpenAPIConfig.
- Reuse or wrap the OpenAPI example generation utility if accessible. If not accessible, implement a small adapter around Polyfactory (via litestar openapi or polyfactory import) to generate sample payloads based on FieldDefinition.
- Attach generated examples to Message.examples or Schema.examples and optionally include a “generated automatically” marker if the UI supports it.

Pros: Strong parity, consistent configuration, better developer experience.
Cons: Requires new dependencies or careful reuse of existing OpenAPI internals, risk of API mismatch.

### Approach C: Full OpenAPIConfig mirroring
- Mirror OpenAPIConfig and allow the AsyncAPI plugin to share a subset of the configuration object or utilities.
- Integrate Litestar’s OpenAPI schema generation pipeline for shared schema definitions, including use of DTO annotations, docstrings, and examples.

Pros: Maximum parity.
Cons: Higher complexity, may introduce tight coupling with OpenAPI modules and reduce independence of AsyncAPI plugin.

Given the current architecture and the request for parity, Approach B is a likely target: add config toggles, read handler metadata/docstrings, generate examples with Polyfactory or litestar openapi helpers, and attach them to message schemas. Approach C might be too heavy for the scope and would likely be a separate roadmap item.

## Research Details: Where to source metadata

- **Handler metadata**: Litestar route handlers store configuration in the handler object (summary, description, operation_id, tags). The AsyncAPI extractor already receives a WebsocketRouteHandler instance; it can access `.opt` and may access `route_handler.summary`, `route_handler.description`, or `route_handler.operation_id` depending on Litestar version. We must verify which attributes exist and whether they are stable. If not, we may need to use a helper to read OpenAPI metadata or to check handler kwargs stored in `.opt`.

- **Docstrings**: If `use_handler_docstrings` is enabled, we should parse `route_handler.fn.__doc__` or `handler.fn.__doc__` (depending on wrapper). The OpenAPI implementation likely uses a docstring utility; replicating the logic ensures consistent formatting (strip indentation, keep first paragraph as summary?). The docstring should probably fill description if summary is already set or if summary is empty, using the same heuristics OpenAPI uses.

- **Examples**: Options include:
  - Use Litestar OpenAPI schema generation example utilities if they are in public API.
  - If not, integrate Polyfactory directly and generate simple example objects from model classes. This implies a new optional dependency or reusing the same polyfactory dependency in litestar (if already a dependency in Litestar itself).
  - Use annotations: `FieldDefinition.kwarg_definition` may have `.example`, `.examples`, `.default` or other metadata; if those exist, prefer them.
  - Provide an override path: allow AsyncAPI decorators to attach message examples explicitly.

## Research Details: Where to store examples

- **Message.examples**: The AsyncAPI UI typically displays message examples. Storing there is the most visible and aligns with the “Message payload example” UI output. If multiple examples exist, place them here.

- **Schema.examples**: This could be used for single or multiple examples when messages are reused or when the message reference points to a schema. In the current generator, messages are often created per operation, and the payload is a schema or reference. If we generate examples at the schema level, the AsyncAPI UI may still render them, but it might not show them under “Message” unless it resolves schemas.

- **Combination**: For auto-generated examples, we can set Message.examples to a list of example payloads. For explicit user-provided examples at the schema level, maintain Schema.examples (if provided by FieldDefinition or inlined schema). Avoid duplicates or conflicting examples.

## Research Details: When to generate examples

- Only generate examples if `create_examples` is enabled in AsyncAPIConfig.
- If `create_examples` is a factory, use it. If a dict, map model types to factories.
- Use deterministic output with `random_seed` if provided, mirroring OpenAPI behavior.
- Respect explicit overrides: if a message already has `examples` via decorators, or schema has examples or example fields, do not overwrite unless specified.

## Edge cases to consider

- **Stream handlers**: A stream handler yields payloads; it may not have an input payload. Example generation should apply to send payloads in the stream operations only.

- **Listener handlers with no return**: Should only generate receive message examples; avoid send example generation when return type is None.

- **Reference schemas**: If payload schema is a Reference, we may need to generate example based on the underlying schema definition; the SchemaRegistry has access to FieldDefinition when building references, but the code may need to track this mapping to produce examples.

- **TypedDict, dataclasses, msgspec, Pydantic**: The schema generator already supports these types via schema plugins; example generation must support the same type sets or degrade gracefully (returning simple example values or skipping).

- **Default values**: If a schema has a default, the generated example should prefer that default or include it. The schema generator already sets default values; we can reuse this for example creation where possible.

- **Enum / Literal**: Example generation should use one of the enum values or literal value, matching OpenAPI behavior and schema constraints.

## Research Details: Testing patterns

The tests in the codebase show a consistent pattern: function-based tests with pytest.anyio and fixtures in conftest. For new features, tests should follow these patterns. Example generation and docstring usage can be tested by building a small Litestar app with a websocket handler with a docstring, then calling AsyncAPIGenerator and inspecting the resulting operation/message description and examples. Tests should also cover overrides and precedence rules (decorator overrides should win over docstring or auto-examples).

## Research Summary and Recommendations

The AsyncAPI plugin is architecturally prepared for metadata enrichment, but lacks the integration with Litestar’s OpenAPI-style features (docstrings, handler metadata, example generation). The AsyncAPI spec and the plugin’s message schema support the same core metadata that OpenAPI uses. The recommended path is to implement configuration flags that mirror OpenAPIConfig, use those flags to read handler metadata and docstrings in the websocket extractor, and add example generation in the schema generator or during discovered message creation. Example injection should prioritize user overrides, then schema defaults, then generated examples. The task will require additions to config.py, extractors, schema generation utilities, and tests.

This plan should proceed with caution regarding dependencies on Litestar internal OpenAPI utilities. If OpenAPI example generation utilities are not public, the AsyncAPI plugin should include a small adapter that uses Polyfactory when enabled and skip example generation otherwise.

## Open questions

- What is the correct Litestar API surface for reading handler-level summary/description/operation_id in websocket handlers? Does it differ for listener vs. stream handlers?
- Should AsyncAPIConfig mirror all OpenAPIConfig fields (tags, security, etc.) or only the subset relevant to docstrings and examples?
- Should message examples be stored at Message.examples, Schema.examples, or both?
- What precedence should exist between decorator overrides, handler metadata, docstrings, and generated examples?

## Source References Used

- Litestar OpenAPIConfig reference, including create_examples, random_seed, and use_handler_docstrings options.
- Litestar OpenAPI docs describing schema generation and UI plugins.
- AsyncAPI 3.0 specification for Message and Schema objects and example fields.
