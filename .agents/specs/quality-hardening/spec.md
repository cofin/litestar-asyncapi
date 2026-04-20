# Spec: Quality Audit & Hardening (Zero-Ambiguity Refinement)

This flow focuses on auditing the existing `litestar-asyncapi` implementation against the "bulletproof" mandate, ensuring strict AsyncAPI 3.0 compliance, canonical alignment with Litestar's upstream patterns, and robust test coverage.

## Problem Statement

The plugin is functional but duplicates many patterns from Litestar's OpenAPI implementation. To ensure long-term maintainability and correctness, we must align our discovery and schema generation logic with Litestar's canonical approaches and implement missing AsyncAPI 3.0 high-fidelity features like `prefixItems`.

## Objectives

- **Canonical Discovery:** Audit and align discovery logic with Litestar's path-item extraction (handling nested routers and layered metadata).
- **Upstream Alignment:** Replace local type-inference and constraints logic with Litestar's internal utilities where they are more robust.
- **Tuple Fidelity:** Implement `prefixItems` for fixed-length tuples.
- **Parameter Compliance:** Implement restricted schema filtering for AsyncAPI v3 parameters.
- **Operation ID Hardening:** Add case-insensitive collision detection and a "strict" config option.
- **Test Coverage:** Reach 90%+ coverage across all core `asyncapi/` modules.
- **UI Safety:** Ensure all dynamic content in renderers is safely escaped.

## Implementation Plan (Worksheet)

### Phase 1: Canonical Audit & Technical Gap Analysis

#### Task 1.1: Audit WebSocket Discovery Alignment
- [x] **Location:** `src/litestar_asyncapi/asyncapi/extractors/websocket.py` [dd2ecf7]
- **Logic Change:**

    - Mirror Litestar's `PathItemFactory.create_path_item`.
    - Check if `WebsocketRouteHandler` has `include_in_schema` in `opt` (since it's missing from the class definition).
    - If missing from `opt`, default to `True` (mirroring Litestar's `resolve_include_in_schema`).
    - Audit `_path_parameters_to_parameters`: Ensure it uses `PathParameterDefinition` correctly (mirroring `litestar._openapi.parameters.create_parameters_for_handler`).

#### Task 1.2: Audit Operation ID Uniqueness & Config
- [x] **Location:** `src/litestar_asyncapi/asyncapi/generator.py`, `src/litestar_asyncapi/config.py` [8b5722f]
- **Logic Change:**
    - Update `_ensure_unique_operation_id` to use `casefold()` for collision detection.
    - Update `AsyncAPIConfig` to add `strict_uniqueness: bool = False`.
    - If `strict_uniqueness` is True, raise `ImproperlyConfiguredException` on collision instead of suffixing.

#### Task 1.3: Audit Schema Redundancy & Tuple Mapping
- [x] **Location:** `src/litestar_asyncapi/asyncapi/schema_generation/schema.py`, `utils.py`
- **Logic Change:**
    - Identify local predicates to replace with `litestar.utils.predicates.is_class_and_subclass`, `is_optional_union`, etc.
    - Plan `prefixItems` implementation for fixed-length tuples (AsyncAPI 3.0 specific).
    - Plan `_filter_parameter_schema_v3`: Restricted fields for Parameters: `type`, `format`, `enum`, `description`, `default`, `examples`, `minimum`, `maximum`, etc. (Strip `title`, `required`, `deprecated` from the schema itself as they are on the Parameter object).

### Phase 2: Implementation of Gaps & Alignment

#### Task 2.1: Implement High-Fidelity Tuple Mapping
- [x] **Location:** `src/litestar_asyncapi/asyncapi/schema_generation/schema.py` [21c5eaa]
- **Change:**
    - In `generate_schema` for `origin is tuple`:
    - If fixed-length (not `...`), use `prefixItems` instead of `items` with `one_of`.
    - Set `minItems` and `maxItems` based on tuple length.

#### Task 2.2: Implement Parameter Schema Filtering
- [x] **Location:** `src/litestar_asyncapi/spec/channel.py` [2d64a52]
- **Change:**
    - Refactored `Parameter` to align with AsyncAPI 3.0.0 (removed `schema`, added `enum`, `default`, `examples`).
    - Updated extractors to populate `description` with type info instead of a full schema.

#### Task 2.3: Integrate Litestar Internal Utilities
- [x] **Location:** `src/litestar_asyncapi/asyncapi/schema_generation/schema.py`, `utils.py` [5d75f0b]
- **Change:**
    - Replace `split_optional_union` with `litestar.utils.typing.make_non_optional_union` and `is_optional_union`.
    - Replace local type-mapping logic with `litestar.utils.helpers.get_name` for component keys.

#### Task 2.4: Fix Discovery Gaps (Include In Schema)
- [x] **Location:** `src/litestar_asyncapi/asyncapi/extractors/websocket.py` [dd2ecf7]
- **Change:**
    - Implement `_should_include_handler(handler: WebsocketRouteHandler) -> bool`.
    - Look for `include_in_schema` in `handler.opt`.

#### Task 2.5: Implement Strict Operation ID Mode
- [x] **Location:** `src/litestar_asyncapi/asyncapi/generator.py` [8b5722f]
- **Change:**
    - Enforce Config's `strict_uniqueness`.

#### Task 2.6: Secure UI Renderers
- [x] **Location:** `src/litestar_asyncapi/plugins.py` [f559872]
- **Change:**
    - Ensure all dynamic values (title, description) passed to HTML templates are escaped using `html.escape`.
    - Implemented `escapeHtml` helper in playground JS and used it for channel info and message history.

### Phase 3: Verification & Coverage

#### Task 3.1: Reach 90%+ Test Coverage
- [x] **Location:** `src/litestar_asyncapi/asyncapi/` [c526a35]
- **Action:**
    - Add tests for `tag.py` and `correlation_id.py` specifically.
    - Add tests for new `prefixItems` and `strict_uniqueness` logic.

#### Task 3.2: Integration Test for Nested Routers
- [x] **Location:** `tests/integration/test_discovery.py` [6509bab]
- **Action:**
    - Create a test case with nested Routers and verify WebSocket discovery.

#### Task 3.3: Manual Verification Protocol
- [x] **Action:**
    - Execute the manual verification protocol defined in `workflow.md`. [b4e8809]

## Acceptance Criteria
- [ ] 100% AsyncAPI 3.0.0 meta-schema validation for generated documents.
- [ ] 90%+ code coverage for `src/litestar_asyncapi/asyncapi/`.
- [ ] No `operationId` collisions across 100+ simulated reloads.
- [ ] `tuple[int, str]` renders as `prefixItems: [{type: integer}, {type: string}]`.
- [ ] Parameter schemas do not contain `title` or `deprecated` (v3 restriction).
