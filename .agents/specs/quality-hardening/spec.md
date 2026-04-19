# Spec: Quality Audit & Hardening (Revised)

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

## Implementation Plan

### Phase 1: Canonical Audit & Gap Analysis

- [ ] Task: Audit `extract_websocket_channels` against Litestar's `litestar._openapi.path_item` logic.
    - [ ] Verify nested router discovery.
    - [ ] Verify layered metadata/guard handling.
- [ ] Task: Audit `operationId` generation.
    - [ ] Verify uniqueness across multiple channels.
    - [ ] Verify stability and case-insensitivity.
- [ ] Task: Audit schema generation logic for redundancy.
    - [ ] Identify `TYPE_MAP` entries that can be more canonical.
    - [ ] Identify local predicates to replace with `litestar.utils.predicates`.
- [ ] Task: Audit AsyncAPI v3 compliance.
    - [ ] Verify parameter schema field restrictions.
    - [ ] Verify tuple mapping fidelity.

### Phase 2: Implementation of Gaps & Alignment

- [ ] Task: Fix `operationId` gaps and add `strict_uniqueness` config option.
- [ ] Task: Implement `prefixItems` for `tuple[int, str]` mapping.
- [ ] Task: Implement parameter schema filtering for v3 compliance.
- [ ] Task: Integrate Litestar internal utilities to reduce redundant code.
- [ ] Task: Fix identified gaps in discovery (nested routers/guards).
- [ ] Task: Ensure all UI renderers use `html.escape`.

### Phase 3: Verification & Coverage

- [ ] Task: Reach 90%+ test coverage for `src/litestar_asyncapi/asyncapi/`.
- [ ] Task: Implement integration tests for nested router discovery.
- [ ] Task: Implement verification tests for strict AsyncAPI 3.0 validation.

- [ ] Task: Flow - User Manual Verification 'Quality Audit & Hardening' (Protocol in workflow.md)
