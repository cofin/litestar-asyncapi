# Recovery Guide: PRD-006 Advanced Features

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**Created**: 2025-12-17
**Status**: Not Started

---

## Quick Resume

1. Read `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/prd.md`
2. Use `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/tasks.md` as the checklist
3. Confirm PRD-003 extractor outputs are stable
4. Implement decorators + override policy first, then traits and optional bindings

---

## Primary References

- `litestar/handlers/base.py` and route handler `opt` metadata usage (pattern)
- `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md` (inference behavior)

---

## Completion Criteria

- Decorators can fully document a plain websocket handler (no inference required).
- Extractors behave deterministically and follow precedence rules.
