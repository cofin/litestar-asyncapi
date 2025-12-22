# Recovery Guide: PRD-004 Document Generation

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Quick Resume

1. Read `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md`
2. Use `specs/active/asyncapi-plugin/prds/prd-004-document-generation/tasks.md` as the checklist
3. Confirm PRD-001..003 are complete and tested
4. Implement generator class, then wire it into config/plugin, then add integration tests

---

## Primary References

- `litestar/_openapi/plugin.py` (build/caching strategy)
- `litestar/openapi/config.py` (config → spec construction)

---

## Next Step

After PRD-004 is complete, proceed to:
- `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/prd.md`

---

## Implementation Status

- Quality gates: `make test` PASS, `make lint` PASS, generator coverage ≥ 90% PASS
- Core implementation:
  - `src/litestar_asyncapi/_asyncapi/generator.py` (AsyncAPI orchestration)
  - `src/litestar_asyncapi/config.py` (generation settings + server conversion)
  - `src/litestar_asyncapi/plugin.py` (cached document/schema accessors)
  - `src/litestar_asyncapi/_typing.py` (optional dependency flags/shims)
- Tests:
  - `src/tests/unit/test_generator.py`
  - `src/tests/unit/test_generator_components.py`
  - `src/tests/unit/test_config.py`
  - `src/tests/integration/test_full_generation.py`
  - `src/tests/integration/test_plugin_cache.py`
