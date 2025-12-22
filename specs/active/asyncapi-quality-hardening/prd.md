# PRD: AsyncAPI Quality Hardening for Litestar

## Intelligence Context

### Complexity Assessment

This feature is classified as **Complex**. It spans multiple subsystems (route discovery, schema generation, component naming, renderer output, and testing), requires careful alignment with an external specification (AsyncAPI 3.0), and affects multiple files. The effort is not a single-file change and introduces cross-cutting quality guarantees, so the checkpoint target is **10+**.

### Similar Features Identified

1. `src/litestar_asyncapi/_asyncapi/generator.py` - Core AsyncAPI document assembly and operation generation.
2. `src/litestar_asyncapi/_asyncapi/extractors/websocket.py` - WebSocket discovery and operation inference logic.
3. `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py` - Type-driven schema generation and plugin integration.
4. `src/litestar_asyncapi/plugin.py` - InitPluginProtocol integration and docs router.
5. `src/tests/unit/test_generator.py` - Example of generator behavior and operation expectations.

### Patterns to Follow

- InitPluginProtocol class pattern for app integration.
- Dataclass schema object pattern for spec objects with `to_schema()` output.
- Schema plugin pattern (`supports()` + `populate_component_schema()`).
- Function-based tests with `pytest.mark.anyio` and inline Litestar app creation.
- Error handling using `ImproperlyConfiguredException` for invalid user inputs.

## Problem Statement

The current AsyncAPI plugin implementation is feature-complete for basic usage but has several quality gaps that can produce inaccurate or noncompliant documents. These issues limit the plugin’s usefulness for production documentation and tooling that expects the AsyncAPI 3.0 document structure to be correct and stable.

The observed issues include:

- Non-unique `operationId` values for channels discovered via ChannelsPlugin, which can cause ambiguity in code generation.
- Schema generation that omits constraint details and misrepresents tuple types.
- Component key overrides that are not validated or normalized, potentially producing invalid `$ref` paths.
- UI rendering that does not escape HTML in the title, allowing unintended markup injection.
- Some AsyncAPI v3-specific structure expectations are not fully reflected (e.g., operation messages referencing channel messages).

These problems do not necessarily break documentation for small apps, but they reduce trustworthiness and can break downstream consumers that rely on deterministic operation IDs or strict schema validation. The problem is compounded by incomplete test coverage for these edge cases, which increases the risk of regressions.

The objective of this PRD is to define a comprehensive hardening plan that improves correctness and spec alignment while preserving the existing architecture and public API patterns.

## Goals and Non-Goals

### Goals

1. Improve correctness of operation ID generation and ensure uniqueness where expected.
2. Increase schema generation fidelity, especially for tuple types and field constraints.
3. Enforce safe and deterministic component naming and reference behavior.
4. Ensure UI output is safe from basic HTML injection.
5. Expand test coverage to include the new edge cases and regressions.
6. Maintain existing plugin integration patterns and API shape.

### Non-Goals

- Introducing new protocol bindings or major new AsyncAPI features.
- Redesigning the entire discovery pipeline.
- Migrating to a new schema generation engine or dependency.
- Changing public API signatures in breaking ways.

## User Stories

1. As a developer generating AsyncAPI docs, I want all operation IDs to be unique so code generators and tooling can map them to stable identifiers.
2. As a developer using typed payloads, I want tuples and constraints to be reflected accurately in the AsyncAPI schema so documentation matches runtime validation.
3. As a maintainer, I want component keys to be sanitized to prevent invalid references and avoid runtime errors in tooling.
4. As a security-conscious user, I want the UI to safely render titles without allowing unexpected HTML injection.
5. As a QA engineer, I want tests that exercise these edge cases so I can trust regressions will be caught.

## Success Criteria

- The AsyncAPI document always assigns unique `operationId` values across all operations when ChannelsPlugin discovery is involved.
- Tuple schema generation correctly models fixed-length tuples and variadic tuples instead of using only the first item type.
- Schema constraints from Litestar’s FieldDefinition (min/max, length, pattern, etc.) are propagated into generated schemas where applicable.
- Component key overrides are sanitized or rejected with a clear error if invalid.
- UI output escapes the title to prevent HTML injection.
- Tests exist for each of the above, and coverage for modified modules is 90%+.

## Acceptance Criteria

### Operation ID Uniqueness

- When ChannelsPlugin discovery produces multiple channels, each operation has a unique `operationId` value.
- Operation keys remain stable and deterministic for a given set of channels.
- Duplicate operation IDs from user-specified overrides are detected and either normalized with deterministic suffixing or rejected with a clear error.

### Schema Generation Fidelity

- Fixed-length tuples (e.g., `tuple[int, str]`) are represented using an array schema with ordered `prefixItems` (or `items` with `minItems` and `maxItems` consistent with AsyncAPI JSON Schema rules, depending on the chosen approach).
- Variadic tuples (e.g., `tuple[int, ...]`) are represented as homogeneous arrays with the element type schema.
- If Litestar FieldDefinition includes constraints (min/max, length, regex, etc.), those constraints are applied to the generated schema where they map to AsyncAPI/JSON Schema.

### Component Key Normalization

- `schema_component_key` overrides are normalized to a safe, predictable component name.
- Any invalid characters are either replaced or rejected with a clear `ImproperlyConfiguredException` that references the invalid key.
- `$ref` paths are consistent and stable after normalization.

### UI Renderer Safety

- The UI renderer escapes HTML in the title and any other string interpolations that render into HTML.
- Existing functionality and appearance remain unchanged for normal titles.

### Testing

- New unit tests cover tuple schemas, constraint propagation, component key overrides, and operation ID uniqueness.
- New integration tests cover nested router discovery to validate behavior under real app composition.
- Tests follow the project’s function-based pytest conventions and use `pytest.mark.anyio`.

## Technical Approach

### 1) Operation ID Uniqueness Strategy

The generator should ensure operation IDs are unique across the document, not just the keys in the `operations` map. The operations map is keyed by a sanitized version of the operation ID and does not guarantee uniqueness of `operationId` values. For ChannelsPlugin discovery, operations currently share a static operation_id. The approach should include:

- Update ChannelsPlugin discovery to generate operation IDs per channel. For example, `channels_send_{channel_name}` or `channels_send_{index}` using a deterministic ordering.
- Ensure the generator checks for duplicate operationId values. If duplicates are found, apply deterministic suffixing or raise an error depending on configuration. A configuration option could allow lenient behavior, but a strict mode is preferable for quality hardening.
- Maintain stable ordering to keep suffixes deterministic.

This change should be contained to `extract_channels_plugin_channels()` and/or `AsyncAPIGenerator.build_asyncapi()` to avoid breaking other discovery logic.

### 2) Schema Generation Enhancements

The schema generator should be extended to correctly handle tuple types and to incorporate constraints from FieldDefinition.

Tuple handling:

- If the tuple is fixed-length (e.g., `tuple[int, str]`), produce a schema that captures ordered items. If AsyncAPI JSON Schema supports `prefixItems`, use that. If not, map to `items` with `minItems` and `maxItems` and document the limitation.
- If the tuple is variadic (e.g., `tuple[int, ...]`), use `items` with the element type schema, and allow any length.

Constraints:

- Extract constraint metadata from FieldDefinition and map it to Schema properties. Examples include `min_length`, `max_length`, `pattern`, `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`, etc.
- Ensure constraints are only applied when appropriate for the schema type (e.g., length constraints for string, numeric constraints for numbers, etc.).
- Maintain compatibility with model plugins (pydantic/attrs/dataclass/etc.) by applying constraints at the leaf-level schemas, not necessarily to component references.

A reasonable implementation approach is to add a constraint application function in `schema_generation/utils.py` and call it from `AsyncAPISchemaGenerator.generate_schema()` before returning the schema. For schemas that are references, constraints may need to be applied at the component schema level by the plugins.

### 3) Component Key Sanitization

When a user overrides `schema_component_key`, the value should be normalized to the same character rules applied to generated keys. The normalization should:

- Replace invalid characters with underscores.
- Trim leading and trailing underscores.
- Reject empty results, raising `ImproperlyConfiguredException` with a clear message.

This can be implemented in `_get_component_key_override()` or in `_get_normalized_schema_key()` in `SchemaRegistry`. The normalization should be consistent with the operation ID and schema key sanitization logic.

### 4) Parameter Schema Compliance

AsyncAPI v3 restricts the parameter schema fields. The plugin currently uses a full Schema object for parameters. The hardening effort should decide whether to:

- Enforce a restricted schema subset for parameters, or
- Keep the current behavior but document the deviation.

Given this is a quality hardening effort, the preferred approach is to constrain parameter output to the allowed subset. This can be implemented by adding a dedicated `ParameterSchema` type or by filtering the Schema object before assigning it to a Parameter. For minimal change, implement a filter function that only keeps allowed properties.

### 5) Operation Messages Structure

AsyncAPI expects operations to reference messages defined on channels. The plugin currently attaches messages directly on operations. This PRD treats this as an optional enhancement since it may be more invasive. The work may include:

- Creating deterministic message IDs for discovered messages, adding them to `Channel.messages`.
- Updating `Operation.messages` to reference those message IDs.
- Preserving current behavior if no message IDs are generated.

This work is optional but would improve strict spec compliance. The PRD should call out this change as a conditional feature if time permits or if strict compliance is required by stakeholders.

### 6) UI Renderer Safety

The UI renderer should escape HTML in the title. The simplest approach is to use `html.escape()` on the title before interpolating. This is a minimal change and does not affect normal titles. It should be included in the hardening tasks as a low-risk improvement.

## Testing Strategy

Testing must be expanded to cover the new behavior and prevent regressions. The testing strategy includes unit and integration tests.

### Unit Tests

1. **Operation ID uniqueness**
   - Create a ChannelsPlugin setup with multiple channels and ensure unique operationId values.
   - Ensure deterministic suffixing or naming based on channel name.

2. **Tuple schema generation**
   - `tuple[int, str]` yields an ordered schema with correct item types and appropriate item count limits.
   - `tuple[int, ...]` yields a homogeneous array schema with item type int.

3. **Constraint propagation**
   - Provide FieldDefinition instances with known constraints and assert the schema includes them.
   - Use types where constraints apply (strings, numbers).

4. **Component key overrides**
   - Provide a schema_component_key with invalid characters and verify normalization or error.
   - Ensure `$ref` paths are valid and stable after normalization.

5. **UI escaping**
   - Provide a title containing HTML and ensure output is escaped.

### Integration Tests

1. **Nested routers**
   - Create a Litestar app with nested routers that include WebSocket routes and confirm discovery includes them.

2. **Full document structure**
   - Generate a full document and assert that messages and operations are wired correctly (especially if operation message references are updated).

### Coverage Targets

- 90%+ coverage for modified modules.
- Ensure that new tests are explicitly tied to each change for traceability.

## File Changes

### Files to Modify

- `src/litestar_asyncapi/_asyncapi/extractors/channels.py`
  - Generate unique operation IDs per channel; adjust placeholder message config if needed.

- `src/litestar_asyncapi/_asyncapi/generator.py`
  - Enforce operationId uniqueness across operations and potentially add message reference handling.

- `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py`
  - Improve tuple handling and apply constraints.

- `src/litestar_asyncapi/_asyncapi/schema_generation/utils.py`
  - Add helpers for constraint mapping and tuple schema creation.

- `src/litestar_asyncapi/_asyncapi/datastructures.py`
  - Normalize component key overrides and enforce valid schema component names.

- `src/litestar_asyncapi/plugins.py`
  - Escape HTML title in UI renderer.

### Files to Add or Expand Tests

- `src/tests/unit/extractors/` (new or expanded tests)
- `src/tests/unit/schema_generation/` (new tests for tuple and constraints)
- `src/tests/unit/test_generator.py` (additional generator assertions)
- `src/tests/integration/test_discovery.py` (nested router discovery)
- `src/tests/unit/test_ui_plugin.py` (HTML escaping test)

### Estimated Impact

- 6-10 files modified.
- 8-12 new tests added.
- Some shared utilities updated.

## Risks and Mitigations

- **Risk**: Strict parameter schema filtering may remove details developers expect.
  - **Mitigation**: Document the constraint and ensure a clear error or warning if unsupported fields are discarded.

- **Risk**: Changes to operationId generation might affect existing users who rely on specific values.
  - **Mitigation**: Provide deterministic naming and document the new scheme; optionally add a configuration toggle for legacy behavior.

- **Risk**: Tuple schema adjustments may depend on JSON Schema features not supported in AsyncAPI tooling.
  - **Mitigation**: Use widely supported constructs (items + minItems/maxItems) if `prefixItems` is not safe.

- **Risk**: Component key sanitization could alter existing refs.
  - **Mitigation**: Limit changes to override keys, and document behavior. If invalid keys were used before, the new error path is acceptable because the old behavior was invalid.

## Rollout Plan

1. Implement changes in small increments, starting with operation IDs and schema generation.
2. Add tests in parallel with changes to ensure coverage.
3. Validate document output using integration tests.
4. Update documentation or README notes if new behavior affects users.

## Dependencies

- Litestar (existing dependency) for routing and plugin interfaces.
- AsyncAPI 3.0 specification as authoritative reference for document structure.

## Appendix: Clarification on Route Discovery

Litestar’s router registration behavior flattens nested routers into the app’s `routes` list after registration. This indicates that discovery based on `app.routes` should include nested router WebSocket routes. Still, tests should assert this behavior to prevent regressions if Litestar changes its internal routing behavior in future versions.

## Detailed Requirements

This section enumerates the detailed functional and non-functional requirements by subsystem. These requirements expand on the acceptance criteria and provide traceability from the problem statement to concrete implementation work.

### Discovery and Operation Identification

- The system must generate stable, deterministic operation identifiers for all discovered operations. Determinism is defined as producing the same operationId for the same set of channels and handlers across runs, assuming the input app configuration does not change.
- For ChannelsPlugin discovery, the operationId must include channel context. If channel names are known, the operationId should include the channel name. If channel names are dynamic (arbitrary channels allowed), the operationId should include a descriptive suffix indicating the parameterized channel (e.g., `channels_send_channel_name`).
- The operation key in `document.operations` must remain derived from the operationId, but the operationId itself should be validated for uniqueness. If a duplicate is detected, the system must apply a deterministic suffix or raise an error. The decision should be explicitly documented.
- The system should be resilient to user-specified operation_id values that collide. If a collision occurs, the error message must describe the conflicting operation IDs and the channels involved.
- The AsyncAPI v3 operations object uses operationId as the **map key**, so the implementation must ensure the operationId value (if kept as a field) remains consistent with the key or consider removing the field for strict compliance.

### Schema Generation: Tuples

- Fixed-length tuples should be modeled explicitly, not approximated as homogeneous arrays. The generator should use ordered item definitions where supported.
- If `prefixItems` is used, it must include the correct number of item schemas, and `items` should be set to `False` or a restrictive schema that prevents extra items if strict alignment is desired.
- If `prefixItems` is not used, the generator should approximate the fixed-length tuple using `items` set to a union of the element schemas and set `minItems` and `maxItems` to the tuple length. This is less precise but compatible with older tooling.
- Variadic tuples should use `items` with a single schema and should not set a `maxItems` constraint unless additional constraints are inferred.

### Schema Generation: Constraints

- The schema generator must propagate constraints from FieldDefinition when they map to JSON Schema fields. This includes:
  - `min_length` -> `minLength` for strings.
  - `max_length` -> `maxLength` for strings.
  - `pattern` -> `pattern` for strings.
  - `min_items` -> `minItems` for arrays.
  - `max_items` -> `maxItems` for arrays.
  - `unique_items` -> `uniqueItems` for arrays.
  - `minimum` / `exclusive_minimum` -> `minimum` / `exclusiveMinimum` for numbers.
  - `maximum` / `exclusive_maximum` -> `maximum` / `exclusiveMaximum` for numbers.
  - `multiple_of` -> `multipleOf` for numbers.
- If a constraint is incompatible with the inferred schema type, it should be ignored with an optional debug log, but not cause a failure.
- Constraint propagation should not overwrite existing constraints set by model plugins unless the plugin explicitly leaves them unset. The precedence rules must be documented.

### Component Key Normalization

- Component key overrides should be sanitized to allow only characters that are safe for JSON Pointer references (letters, digits, dot, dash, underscore).
- Invalid characters must be replaced with underscores. Multiple adjacent invalid characters should collapse into a single underscore to keep names readable.
- If a sanitized key is empty or becomes an underscore-only key, the system must raise `ImproperlyConfiguredException` with a message that includes the original key.
- Sanitization should be applied consistently in both component key generation and in reference creation to ensure `$ref` targets match component names.

### Parameter Schema Compliance

- Parameter schemas must be limited to fields supported by AsyncAPI v3. The implementation should either:
  - Filter out unsupported fields before serialization, or
  - Use a dedicated parameter schema type with restricted fields.
- If filtering is used, the plugin should keep a minimal subset of schema fields (type, format, enum, default, examples, description) to remain compliant.
- When parameters are generated from path parameters, the parameter `location` must be set to `path` and must be omitted if not supported by AsyncAPI (if required by spec). The model should align with the specification’s allowed fields.

### Operation Messages and Channel Messages

- If operation messages are updated to reference channel messages, the system must generate stable message keys and include them in channel definitions.
- Each discovered message should map to a channel message entry with a deterministic ID, ideally derived from handler name and action.
- The `Operation.messages` list should include references to those channel messages rather than inline message objects.
- If this change is considered too invasive for the current cycle, the PRD must explicitly defer it and document its limitations.

### Renderer Safety

- The UI renderer must escape any interpolated user content in HTML. This includes the title and any other string values that may be added later.
- Escaping should use the standard library to avoid introducing new dependencies.

## Backward Compatibility

The changes proposed are primarily additive or correctness-focused, but some behaviors may impact existing users. The PRD must acknowledge these cases and provide mitigation or communication strategies.

- **OperationId changes**: Users who rely on specific operationId values may see different identifiers. This is expected for ChannelsPlugin discovery since it currently generates duplicates. The new identifiers should be deterministic and documented. A configuration option to preserve legacy behavior can be considered but should default to safe unique values.
- **Component key overrides**: Sanitization could alter component names. If users relied on invalid keys, their schemas were already noncompliant; however, this is still a breaking change for those users. The PRD should include a migration note.
- **Parameter schema filtering**: Removing unsupported schema fields could reduce documentation detail. This should be framed as improved spec compliance rather than loss of functionality. If needed, a configuration option could toggle strict vs lenient behavior.

## Edge Cases and Examples

The PRD should document edge cases that have historically caused issues or are likely to be sources of bugs:

- Multiple ChannelsPlugin channels with similar names and how operationId suffixes are generated.
- WebSocket routes with repeated path parameters, including integer, date, and string types.
- Schema generation for nested tuples or tuples inside list/dict types.
- Model schemas with optional fields and default values that affect required lists.
- TypedDict definitions with `Required` and `NotRequired` annotations.
- Titles with HTML tags or special characters to verify escaping.

## Alternative Approaches Considered

### Approach A: Enforce Uniqueness at Discovery Layer

Pros:
- Keeps generator simpler.
- OperationId values are unique by construction.

Cons:
- Discovery logic is spread across multiple extractors; enforcing uniqueness there can lead to duplication of logic.

### Approach B: Enforce Uniqueness at Generation Layer

Pros:
- Centralized logic in generator.
- Allows detection of collisions from all sources, including user overrides.

Cons:
- Requires additional tracking and may alter operationId values late in the pipeline.

Recommended: combine both. Generate unique IDs in discovery where possible and validate globally in the generator to catch collisions from user overrides.

### Tuple Schema Options

- **Use prefixItems**: Most accurate for fixed-length tuples. Risk is limited support in older tooling.
- **Use items + minItems/maxItems**: More widely supported but less precise.

Recommended: implement `prefixItems` if supported by the AsyncAPI JSON Schema dialect in use, with a fallback to `items` if compatibility is needed. Document this choice explicitly.

## Implementation Guidance

The following guidance outlines the expected modifications at a high level. It is not code, but it provides implementation constraints and reasoning.

1. **Channel discovery** should remain best-effort and avoid touching Litestar internals beyond public or semi-public fields already used. Any new access to private fields should be justified in docs.
2. **Schema generator** should remain pluggable. Enhancements should not bypass or duplicate plugin logic. Constraint propagation should be applied in a way that respects plugin population of component schemas.
3. **Error handling** should be consistent with existing style. Use `ImproperlyConfiguredException` for invalid configuration and `ValueError` for malformed inputs not tied to configuration.
4. **Serialization output** should be stable. When sanitizing names or operation IDs, preserve determinism by using consistent ordering and suffixing rules.
5. **Tests** should be added incrementally with a focus on clarity. Each new behavior should have at least one test that fails before the change and passes after.

## Observability and Debugging

While the plugin is not currently instrumented for logging, the PRD should consider minimal diagnostic output where appropriate. For example:

- If constraints are dropped because they do not apply to a schema type, an optional debug-level note could help developers understand output differences.
- When operationId collisions are detected and resolved by suffixing, a debug message could aid in tracing the change.

These should be optional and not introduce new logging dependencies. If logging hooks are not present, this can be deferred.

## Documentation Updates

The quality hardening effort should include documentation updates where behavior changes impact users. Updates should include:

- A README note or changelog entry describing operationId uniqueness changes.
- A brief explanation of schema component key normalization and how to set valid keys.
- A note about parameter schema compliance and any constraints that may be filtered.

If this project uses a changelog or release note system, the PRD should identify the proper file or mechanism for recording these changes.

## Open Questions

- Should strict parameter schema compliance be the default, or should it be configurable?
- Is `prefixItems` acceptable for AsyncAPI tooling compatibility, or should we stick with `items` plus min/max?
- Should operationId collision resolution be strict (error) or lenient (suffix)?
- Should message references be enforced now, or deferred to a later spec compliance milestone?

These questions should be resolved during implementation planning or by maintainer input.
