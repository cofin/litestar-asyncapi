# PRD: OpenAPI Parity for AsyncAPI Metadata, Docstrings, and Examples

## Intelligence Context

### Complexity Assessment
This feature is **complex**. It spans multiple subsystems (config, websocket extraction, schema generation, and spec object assembly), requires alignment with Litestar OpenAPI behavior, and introduces new configuration flags and precedence rules. The implementation will touch 5+ files, add new tests, and refine user-facing behavior in the AsyncAPI UI. Based on the project guidance, this warrants a 10+ checkpoint workflow and a comprehensive PRD.

### Similar Features Identified
The following code paths and patterns are the closest analogs and must be preserved or extended:

1. `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` - Existing discovery logic and decorator override merging for operations and messages.
2. `src/litestar_asyncapi/_asyncapi/datastructures.py` - DiscoveredOperation / DiscoveredMessage representations and their mapping to spec objects.
3. `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py` - Field constraint application and schema shaping based on FieldDefinition / KwargDefinition.
4. `src/litestar_asyncapi/decorators.py` - Manual override surface for operation and message metadata.
5. `src/litestar_asyncapi/_asyncapi/generator.py` - Final assembly of AsyncAPI document, unique operation IDs, and component schema emission.

### Patterns to Follow

- **Dataclass + slots**: internal representations and spec objects use `@dataclass(slots=True)`.
- **Discovery + override flow**: base inference from Litestar handlers, then merge decorator overrides.
- **Schema generation**: centralize schema creation in `AsyncAPISchemaGenerator` and avoid per-site ad hoc schemas.
- **Spec serialization**: BaseSchemaObject handles `to_schema()` and merges `extensions` last.
- **Config-driven**: AsyncAPIConfig is the primary entry for new user settings.
- **Tests**: pytest, function-based tests, anyio marker, and explicit schema assertions.

## Problem Statement

The AsyncAPI plugin currently emits a valid AsyncAPI document, but it lacks key metadata and example functionality that Litestar users expect based on the OpenAPI experience. In Litestar’s OpenAPI pipeline, users can specify summaries, descriptions, tags, and examples directly on route handlers, and they can enable docstring extraction and automatic example generation via OpenAPIConfig. In the AsyncAPI plugin, equivalent features are either missing or only available through custom decorators. As a result:

- Generated AsyncAPI docs are sparse unless users add explicit AsyncAPI decorators.
- Docstrings are ignored even when users document websocket handlers as they would for HTTP handlers.
- Example payloads are missing, which makes the AsyncAPI UI less useful for testing and discovery.
- Developers perceive AsyncAPI documentation as a “second-class” experience relative to OpenAPI.

This gap is particularly visible in the AsyncAPI UI, where OpenAPI-like experiences show payload examples and descriptions. The request is to align AsyncAPI’s metadata and example behavior with Litestar’s OpenAPI generation, while respecting AsyncAPI spec semantics and preserving existing override mechanisms.

## Goals and Non-Goals

### Goals

1. **Docstring extraction parity**: Support `use_handler_docstrings` on the AsyncAPI config and use handler docstrings to populate descriptions when enabled.
2. **Handler metadata mapping**: Read route handler metadata (summary, description, operation_id, tags, etc.) and map it to AsyncAPI operations/messages, with precedence rules that preserve AsyncAPI decorator overrides.
3. **Example generation parity**: Provide a config option similar to OpenAPI’s `create_examples` and `random_seed`, and generate example payloads for message schemas when enabled.
4. **Clear precedence model**: Ensure predictable overrides among docstrings, handler metadata, and AsyncAPI decorators.
5. **Test coverage**: Add tests that verify docstring usage, metadata mapping, and example generation in the generated AsyncAPI schema.

### Non-Goals

- Full OpenAPIConfig mirroring. Only the subset of OpenAPIConfig relevant to metadata/docstrings/examples will be mirrored.
- Replacing or deprecating AsyncAPI decorators. They remain first-class override mechanisms.
- Full UI redesign. The AsyncAPI UI will remain based on the existing AsyncAPI standalone render plugin.

## Users and Stakeholders

- **Primary users**: Litestar developers using websocket handlers who expect documentation parity with their HTTP routes.
- **Secondary users**: Documentation consumers (internal teams, clients) who use the AsyncAPI UI to understand messaging contracts.
- **Maintainers**: litestar-asyncapi maintainers who want a clear config surface and predictable behavior.

## Functional Requirements

### FR1: Configuration Surface

Add AsyncAPIConfig fields that mirror OpenAPI behavior:

- `use_handler_docstrings: bool` (default: False or aligned with OpenAPI default)
- `create_examples: bool | Factory | dict[type, Factory]` (default: False)
- `random_seed: int | None` (default: None)

The AsyncAPIConfig must validate these fields similarly to OpenAPIConfig and expose them as simple dataclass attributes.

### FR2: Docstring Extraction

When `use_handler_docstrings` is True:

- Extract docstrings from websocket handler callables and use them to populate Operation.description or Message.description.
- If both summary and description are empty, docstring should populate description.
- If summary is present, docstring should still populate description unless explicit description exists.
- AsyncAPI decorator overrides must take precedence over docstring-derived values.

### FR3: Handler Metadata Mapping

If the websocket handler provides metadata (summary, description, operation_id, tags) that would be used in OpenAPI, AsyncAPI extraction should map these to the DiscoveredOperation fields. The mapping should be best effort and avoid hard dependency on internal Litestar attributes. If metadata is not available, the current defaults remain.

### FR4: Example Generation

When `create_examples` is enabled, generate example payloads for the message payloads and attach them to AsyncAPI output. The generation should:

- Respect `random_seed` for deterministic output.
- Respect explicit examples provided by the developer via decorator or schema metadata (do not overwrite).
- Support dataclass, msgspec, pydantic, and TypedDict payloads if possible.
- Fail gracefully (skip example generation) when a type cannot be instantiated safely.

### FR5: Precedence Rules

For each metadata field (summary, description, operation_id, examples), the precedence order should be:

1. AsyncAPI decorators (`asyncapi_operation`, `asyncapi_message`)
2. Handler metadata (summary/description/operation_id when present)
3. Docstrings (if enabled)
4. Defaults inferred by the extractor

For examples:

1. Explicit message examples (decorator or message traits)
2. Schema-level examples (from field metadata)
3. Auto-generated examples (if enabled)
4. No examples

### FR6: Testing

New unit tests should cover:

- Docstring extraction for listener and stream handlers.
- Metadata mapping from handler attributes into operation summary/description/operation_id.
- Example generation for a basic payload (dataclass or TypedDict), ensuring example appears in the AsyncAPI output.
- Precedence rules (decorator overrides should not be replaced by docstring or auto-generated values).

## Acceptance Criteria

1. AsyncAPIConfig exposes `use_handler_docstrings`, `create_examples`, and `random_seed` with documented behavior.
2. When `use_handler_docstrings` is enabled, a handler with a docstring results in Operation.description being populated if no decorator override exists.
3. When handler metadata is present (summary/description/operation_id), AsyncAPI uses it in the generated document when no decorator override exists.
4. When `create_examples` is enabled, the AsyncAPI UI shows a payload example for at least one example websocket handler, and the schema output includes examples in either Message or Schema objects.
5. Decorator overrides always take precedence over docstring/handler metadata.
6. Tests demonstrate docstring usage, metadata mapping, example generation, and precedence rules.

## User Stories

1. As a Litestar developer, I can enable `use_handler_docstrings` so my websocket handler docstrings appear in AsyncAPI docs without needing extra AsyncAPI-specific decorators.
2. As a Litestar developer, I can enable `create_examples` and get example payloads for my websocket messages, similar to OpenAPI.
3. As a maintainer, I can reason about precedence rules and trust that explicit AsyncAPI decorators override implicit metadata.
4. As a documentation consumer, I can see summaries, descriptions, and example payloads in the AsyncAPI UI that match the OpenAPI docs quality.

## Technical Approach

### Architecture Fit

The AsyncAPI plugin already follows an extractor/generator architecture that aligns well with the required changes. The enhancements should be introduced with minimal structural disruption:

- Configuration changes in AsyncAPIConfig.
- Metadata extraction enhancements in websocket extractors.
- Example generation integration in schema generation or message creation.
- Optional helpers for docstring extraction and example generation (potentially shared utilities).

### Proposed Implementation Steps

#### 1. Extend AsyncAPIConfig

Add new fields for docstrings and example generation. Model these after OpenAPIConfig naming and semantics so users familiar with OpenAPI will recognize them. Document these fields in the config docstring.

Potential signature additions:

- `use_handler_docstrings: bool = False`
- `create_examples: bool | object | dict[type, object] = False`
- `random_seed: int | None = None`

Note: The exact type of `create_examples` should align with Litestar’s OpenAPIConfig if possible; if OpenAPIConfig uses Polyfactory-based factory types, AsyncAPIConfig should mirror the same union to avoid user confusion.

#### 2. Introduce Docstring Extraction Utility

Add a small utility function in a new module (e.g., `_asyncapi/utils/docstrings.py`) or alongside extractors. The function should:

- Accept a handler callable.
- Extract the docstring via `inspect.getdoc()` or equivalent.
- Normalize whitespace and return a string or None.

If Litestar’s OpenAPI implementation provides a docstring parser, consider reusing it to maintain parity.

#### 3. Map Handler Metadata

Enhance `_infer_listener_operations` and `_infer_stream_operations` to read metadata from the WebsocketRouteHandler. Possible sources:

- `route_handler.summary` and `route_handler.description` if present.
- `route_handler.opt` for OpenAPI-related metadata.
- `route_handler.operation_id` if present.

Because Litestar metadata APIs may evolve, implement a safe, defensive read (use getattr with defaults and type checks). This avoids coupling the AsyncAPI plugin tightly to internal attributes.

#### 4. Integrate Docstrings

When `use_handler_docstrings` is enabled, apply docstrings to operation or message descriptions. The target should be the Operation description by default. If an operation already has a description from metadata or overrides, do not replace it.

Design choice: When a listener has both receive and send operations, the docstring might apply to both or only the receive operation. For simplicity, apply to both operations unless overridden, or add a rule where docstring applies to the receive operation only and the send operation uses a derivative description. This should be specified in the PRD and tested.

#### 5. Example Generation Strategy

Integrate example generation as follows:

- Add a helper that can generate example payloads from FieldDefinition. It should support basic primitives and the same model types supported by schema generation. If OpenAPI uses Polyfactory for this, use that when available.
- Inject examples into DiscoveredMessage (add new field `examples: list[Any] | None`) or directly into Message objects at generation time.
- Favor Message.examples, since the AsyncAPI UI is likely to display message examples directly.
- If FieldDefinition or schema includes examples or defaults, prefer those. For example, if a field default exists, use it as part of example generation.

#### 6. Precedence Rules and Overrides

Implement precedence rules explicitly in the extractor or generator to avoid subtle regressions:

- Decorator overrides should always win.
- If handler metadata provides a summary or description, it should override docstrings but not decorator overrides.
- Docstrings should only be applied if `use_handler_docstrings` is enabled and no explicit description exists.
- Generated examples should only be applied if no explicit examples exist.

#### 7. Update Tests

Add new tests in `src/tests/unit` and possibly an integration test in `src/tests/integration` to validate the full output. Tests should cover:

- A websocket listener with a docstring yields description in AsyncAPI output when `use_handler_docstrings` is True.
- A handler with explicit summary/description metadata (as available in Litestar handlers) yields the same summary/description in AsyncAPI output.
- AsyncAPI decorator overrides override metadata and docstrings.
- Example generation yields Message.examples when enabled and is absent when disabled.

### Detailed Data Flow

The updated flow from handler to AsyncAPI document will be:

1. Discover websocket routes (existing).
2. Build DiscoveredOperation list using handler metadata and docstrings (new data sources).
3. Apply decorator overrides (existing, now with higher precedence).
4. Generate payload schemas (existing).
5. Generate examples if configured and attach to DiscoveredMessage or Message (new).
6. Assemble AsyncAPI document (existing).

### Compatibility Considerations

- Defaults should preserve current behavior unless new config flags are explicitly enabled.
- Existing AsyncAPI decorators should continue to work without changes.
- Schema generation should remain stable for types that do not support example generation.

## Testing Strategy

### Unit Tests

- **Docstring test**: Create a websocket listener with a docstring, build AsyncAPI, verify the operation description matches the docstring when enabled.
- **Metadata test**: Set summary/description on handler (via websocket decorator arguments or equivalent), verify those fields appear in AsyncAPI operation.
- **Precedence test**: Add asyncapi_operation decorator with description/summary, ensure it overrides handler metadata and docstrings.
- **Example generation test**: Enable `create_examples`, build AsyncAPI, verify Message.examples exists for payload and includes expected sample values.
- **No examples test**: With `create_examples=False`, verify no examples exist in message or schema.

### Integration Tests

- Add an integration test that instantiates a Litestar app with a websocket listener and stream, with config toggles enabled, and assert that the serialized AsyncAPI schema has operation descriptions and examples in correct locations.

### Coverage Requirements

Target 90%+ coverage on newly modified modules (`config.py`, websocket extractor, schema generation utilities, any new helper modules). Ensure tests exercise both listener and stream cases.

## File Changes

### Files to Modify

- `src/litestar_asyncapi/config.py`
  - Add new config fields and docstrings.
  - Update any helper methods if needed.

- `src/litestar_asyncapi/_asyncapi/extractors/websocket.py`
  - Add handler metadata extraction and docstring integration.
  - Apply precedence rules before decorator overrides.

- `src/litestar_asyncapi/_asyncapi/datastructures.py`
  - Add examples field to DiscoveredMessage if needed.
  - Update `to_spec_message()` to include examples.

- `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
  - Add example generation utility or integrate with existing schema creation logic.

- `src/litestar_asyncapi/_asyncapi/generator.py`
  - Ensure generated Message objects include examples if provided.

- `src/tests/unit/extractors/` and `src/tests/unit/` files
  - Add tests for docstrings, metadata mapping, and example generation.

### Files to Create

- `src/litestar_asyncapi/_asyncapi/utils/docstrings.py` (if a new helper is needed)
- `src/litestar_asyncapi/_asyncapi/utils/examples.py` (if example generation is separated)
- Additional test files as needed.

### Estimated Changes

- Config additions: 10-20 lines.
- Extractor updates: 60-120 lines.
- Schema/example generation utilities: 80-160 lines.
- Tests: 150-250 lines.

## Risks and Mitigations

- **Risk: Dependency on Litestar internal OpenAPI APIs**
  - Mitigation: Use defensive attribute access and avoid relying on private APIs. Provide fallbacks.

- **Risk: Polyfactory dependency not available**
  - Mitigation: Make example generation optional; if Polyfactory is missing, skip example generation with a warning or silent fallback.

- **Risk: Breaking existing schema output**
  - Mitigation: Default new features to off; ensure no output changes unless flags are enabled.

- **Risk: Conflicting examples**
  - Mitigation: Apply strict precedence rules and avoid overwriting explicit examples.

## Implementation Phases

1. **Config and utilities**: Add config fields and utility helpers for docstrings/examples.
2. **Extractor updates**: Map metadata and docstrings; apply precedence rules.
3. **Example integration**: Generate examples and attach to messages or schemas.
4. **Tests**: Add and validate tests for new behavior.
5. **Docs updates**: Add documentation to README or docs (if needed) describing new settings.

## Open Questions

- Should docstrings apply to both receive and send operations or only to receive operations in listener handlers?
- Where should message examples be stored for best UI compatibility: Message.examples, Schema.examples, or both?
- Should AsyncAPIConfig default `use_handler_docstrings` to match OpenAPI or remain disabled for backward compatibility?
- Are there existing Litestar utilities for example generation that can be reused instead of introducing a new dependency?

## Conclusion

Bringing AsyncAPI metadata and examples to parity with OpenAPI will significantly improve documentation quality and user experience for event-driven APIs in Litestar. The proposed changes align with existing patterns in the codebase, are opt-in via configuration for backward compatibility, and can be tested with deterministic outputs. With clear precedence rules and robust tests, these features can be implemented without destabilizing the current plugin.


## Detailed Requirements and Behavior Notes

### Metadata Extraction Matrix

The AsyncAPI extractor should consider multiple sources of metadata. The following matrix clarifies when each field is populated. Each row describes the source and which fields are eligible to be set. The precedence order described earlier still applies.

- **Route handler attributes**: The handler may expose summary, description, tags, or operation_id as direct attributes. When present, these are treated as primary metadata and should populate DiscoveredOperation. This aligns with OpenAPI behavior where decorator metadata becomes part of the route handler instance.

- **Route handler options (`opt`)**: The handler opt dictionary may include OpenAPI-relevant metadata or plugin-specific metadata. AsyncAPI should not assume OpenAPI-specific keys, but it can look for normalized values if they are stable or documented.

- **Docstrings**: If enabled, docstrings should be normalized with `inspect.getdoc()`, which already dedents and collapses common indentation. The first line or first paragraph may be used as a summary if no summary exists. However, to avoid diverging from OpenAPI behavior, the initial implementation should only fill description and avoid auto-deriving summary unless clearly documented.

- **AsyncAPI decorators**: These are explicit overrides and should be applied last. This is already how the code behaves, but the extractor should ensure it does not overwrite decorator-provided values when introducing new metadata sources.

### Example Generation Matrix

Example generation must be conservative and deterministic. The following rules apply:

- If the AsyncAPI message already includes explicit examples (from decorator overrides or message traits), do not generate new examples. This allows explicit overrides to remain authoritative.

- If the schema object (payload schema) already includes `examples` or `default` values, prefer those and avoid generating a new example. If a single default exists, it can be used as the example payload without invoking a factory.

- If `create_examples` is disabled, skip generation completely and preserve current behavior.

- If `create_examples` is enabled but no suitable factory exists for the payload type, skip generation rather than raising an error. This ensures that enabling examples is safe even for non-standard models.

- If `create_examples` is a mapping of types to factories, prefer the factory for the exact type, then fall back to a generic factory if provided.

### Location of Examples

The AsyncAPI spec allows examples on both Message and Schema. The UI rendering requirements favor Message.examples because the AsyncAPI UI typically renders message examples in a dedicated section. The initial parity implementation should therefore place auto-generated examples at the Message level. The schema-level examples should only be used when explicitly provided by schema metadata or when there is a strong reason to reuse schema examples across multiple messages. This avoids duplicating or conflicting examples.

### Determinism and Randomness

OpenAPI example generation uses a `random_seed` to ensure deterministic output. AsyncAPI example generation should use the same pattern, ensuring that the same payload type yields the same example across runs when a seed is provided. Determinism is critical for tests and for reproducible documentation builds.

### Error Handling

Example generation should not raise runtime errors during app initialization. If a factory throws or a model cannot be constructed safely, example generation should log or ignore the error and continue. The AsyncAPI schema generation should still succeed even if no examples are produced.

## UX and Documentation Considerations

### AsyncAPI UI Experience

The AsyncAPI UI should display richer information when these features are enabled. Specifically:

- Operation descriptions should appear and align with handler docstrings.
- Message payload examples should appear under the message details for each operation.
- If multiple examples exist, they should be displayed as a list. If only a single example exists, the UI should show it as a single payload block.

### Developer Documentation

Developer-facing documentation should describe:

- How to enable docstrings and examples via AsyncAPIConfig.
- The precedence rules for metadata and examples.
- How to supply explicit examples using AsyncAPI decorators.
- The interaction between schema defaults and auto-generated examples.

### Migration Impact

Existing users should not observe any behavior change unless they opt into the new configuration flags. This is a key compatibility requirement. However, any users who already rely on OpenAPI-style metadata might expect it to be used automatically. This is why the PRD specifies an explicit config flag for docstrings and examples.

## Performance Considerations

- Docstring extraction is inexpensive and only done at schema generation time, not per request.
- Example generation may be more expensive if complex models are instantiated. This is mitigated by performing example generation only at schema build time and only when enabled.
- Caching: The AsyncAPI plugin already supports schema caching; example generation should be included in the cache output so the cost is paid once.

## Security and Safety Considerations

- Example generation should avoid executing arbitrary code. If a model includes a default factory or custom validators, a factory may execute user-provided logic. For safety, example generation should only be enabled explicitly by the developer and should be documented as such.
- Docstrings may include sensitive information; users should be aware that enabling docstring extraction will expose those docstrings publicly in AsyncAPI docs.

## Success Metrics

- Documentation completeness: A websocket handler with a docstring and a payload type should generate a schema with descriptions and examples when enabled.
- Developer satisfaction: The AsyncAPI docs should look closer to OpenAPI docs in terms of metadata richness and example availability.
- Compatibility: No changes in generated schema when new config flags are left at defaults.

## Rollout and Release Notes

- Add a release note entry describing the new AsyncAPIConfig flags and the behavior changes when enabled.
- Provide a brief migration guide for users who want to enable the new features.
- Include a “Known limitations” subsection describing any types that do not support example generation.

## Additional Acceptance Criteria (Expanded)

7. When `create_examples` is enabled and a payload model has default values, the example output should reflect those defaults rather than random values.
8. When `create_examples` is disabled, the output should be identical to current schema output (no additional examples).
9. When `use_handler_docstrings` is enabled and summary is empty, description is populated from the docstring, but summary remains unchanged unless explicitly provided.
10. When both handler metadata and docstrings exist, handler metadata takes precedence for summary/description, and docstrings only fill missing fields.
11. When message traits are configured in AsyncAPIConfig and referenced by operations, example generation should not alter trait behavior or result in missing trait references.
