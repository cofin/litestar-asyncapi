# Sub-PRDs: AsyncAPI Plugin

This directory contains the implementation-ready sub-PRDs that make up the parent workspace at
`specs/active/asyncapi-plugin/`.

Each sub-PRD has:
- `prd.md` - phase requirements and technical approach
- `tasks.md` - phase task breakdown with status
- `recovery.md` - quick resume guide
- `research/plan.md` - phase-specific research notes and decisions

## Index

| ID | Title | Status | Docs |
|---:|-------|--------|------|
| 001 | Spec foundation | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md` |
| 002 | Schema generation | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/prd.md` |
| 003 | Handler discovery | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md` |
| 004 | Document generation | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md` |
| 005 | Render plugins | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/prd.md` |
| 006 | Advanced features | COMPLETE | `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/prd.md` |

## How to use

1. Start with `specs/active/asyncapi-plugin/prd.md` for the full vision.
2. Implement one sub-PRD at a time, using its `tasks.md` as the checklist.
3. Update the sub-PRD `tasks.md` and `recovery.md` as work progresses.
