# Recovery Guide: PRD-002 AsyncAPI Schema Generation

**Parent Workspace**: `specs/active/asyncapi-plugin/`
**Created**: 2025-12-17
**Status**: COMPLETE
**Completed**: 2025-12-17

---

## Quick Resume

1. Read `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/prd.md`
2. Use `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/tasks.md` as the checklist
3. Confirm PRD-001 serialization objects exist and are stable
4. Implement schema generator + registry, then add model plugins and tests

---

## Primary References

- `litestar/_openapi/schema_generation/schema.py`
- `litestar/_openapi/datastructures.py::SchemaRegistry`

---

## Next Step

After PRD-002 is complete, proceed to:
- `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md`

---

## Implementation Status

- Quality gates: `make test` PASS, `make lint` PASS
- Core implementation:
  - `src/litestar_asyncapi/_asyncapi/datastructures.py` (schema registry + `$ref` naming)
  - `src/litestar_asyncapi/_asyncapi/schema_generation/schema.py` (AsyncAPISchemaGenerator + TYPE_MAP)
  - `src/litestar_asyncapi/_asyncapi/schema_generation/plugins/*` (attrs/dataclass/msgspec/TypedDict/pydantic plugins)
- Tests:
  - `src/tests/unit/schema_generation/test_registry.py`
  - `src/tests/unit/schema_generation/test_schema_generation.py`
  - `src/tests/unit/schema_generation/test_attrs.py`
  - `src/tests/unit/schema_generation/test_dataclass.py`
  - `src/tests/unit/schema_generation/test_msgspec.py`
  - `src/tests/unit/schema_generation/test_typed_dict.py`
  - `src/tests/unit/schema_generation/test_pydantic.py`
