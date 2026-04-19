## [2026-04-19 10:20] Revision 1

**Type:** both
**Reason:** Alignment with upstream Litestar canonical patterns and leveraging built-in utilities to ensure a "bulletproof" implementation. Acknowledged that breaking changes are acceptable for architectural integrity.

### Changes Made

**Spec Changes:**
- **Objective added:** Canonical Discovery Alignment. Ensure discovery logic matches Litestar's OpenAPI path-item extraction (handling nested routers, guards, and layered metadata).
- **Objective added:** Upstream Utility Integration. Replace local type-checking and schema-shaping logic with more robust Litestar internal predicates and utilities.
- **Objective added:** Technical Fidelity Upgrade. Implement `prefixItems` for fixed-length tuples (AsyncAPI 3.0 specific) and restricted parameter schema filtering.
- **Success Criteria updated:** Established 90%+ test coverage target for all core modules, specifically targeting `src/litestar_asyncapi/asyncapi/`.

**Plan Changes:**
- Added: Task 1.5 - Audit and align `extract_websocket_channels` with Litestar's `path_item` extraction logic.
- Added: Task 1.6 - Identify and replace redundant internal utilities with Litestar's `litestar.utils.typing` and `litestar.utils.predicates`.
- Added: Task 2.6 - Implement `prefixItems` for `tuple` schema generation.
- Added: Task 2.7 - Implement strict AsyncAPI v3 parameter schema filtering.
- Modified: Task 3.2 - Target 90%+ coverage for the entire `asyncapi/` module.

### Impact Assessment

- Tasks affected: Phase 1 (Audit) and Phase 2 (Implementation) expanded with specific technical targets.
- Timeline impact: Moderate increase in effort due to deeper architectural alignment.
- Dependencies updated: Increased reliance on Litestar's internal (but stable) utilities.
