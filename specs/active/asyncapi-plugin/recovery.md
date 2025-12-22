# Recovery Guide: litestar-asyncapi Plugin

**Feature**: AsyncAPI 3.0 Plugin Implementation
**Complexity**: Complex (10+ checkpoints)
**Created**: 2025-12-17
**Status**: PRD Complete - Ready for Implementation

---

## Quick Resume

If resuming work on this feature:

1. Read this file for context
2. Read `prd.md` for full requirements
3. Check `tasks.md` for current progress
4. Open `specs/active/asyncapi-plugin/prds/README.md` to pick the next sub-PRD
5. Continue from the last incomplete sub-PRD `tasks.md`

---

## Session Context

### Complexity Assessment
- **Level**: Complex
- **Checkpoints**: 10+
- **Estimated Files**: 40+
- **Total Sub-PRDs**: 6

### Research Completed
- Litestar OpenAPI architecture analyzed (via gh API)
- AsyncAPI 3.0 specification documented
- FastStream patterns studied
- asyncapi-python patterns reviewed
- WebSocket/Channels integration points mapped

### Key Decisions Made
1. **AsyncAPI 3.0.0 only** - No 2.x support
2. **WebSocket binding primary** - Other protocols future
3. **Mirror OpenAPI pattern** - Consistency with Litestar
4. **Automatic discovery first** - Decorator override optional
5. **CDN-based UI** - Optional bundled assets

---

## Intelligence Context

### Similar Features Identified
1. `litestar/openapi/` - Primary reference
2. `litestar/openapi/spec/` - Spec object pattern
3. `litestar/openapi/plugins.py` - Render plugin pattern
4. `litestar/_openapi/schema_generation/` - Schema generation

### Patterns to Follow
| Pattern | Location | Purpose |
|---------|----------|---------|
| InitPluginProtocol | `plugin.py` | App integration |
| Dataclass config | `config.py` | Configuration |
| Render plugins | `plugins.py` | Output formatting |
| Spec objects | `spec/*.py` | Specification model |
| Schema generation | `_asyncapi/` | Type conversion |

### MCP Tools Needed
- `mcp__context7__get-library-docs` - Litestar docs
- `mcp__pal__planner` - Complex planning
- `mcp__sequential-thinking__sequentialthinking` - Analysis

---

## File Locations

### Workspace
```
specs/active/asyncapi-plugin/
├── prd.md           # Main PRD (3400+ words)
├── tasks.md         # Task breakdown (6 sub-PRDs)
├── recovery.md      # This file
├── prds/            # Sub-PRD workspaces (001-006)
├── research/
│   └── plan.md      # Research document (2100+ words)
├── tmp/             # Working files
└── patterns/        # Extracted patterns
```

### Source (Target)
```
src/litestar_asyncapi/
├── __init__.py      # Public exports
├── config.py        # AsyncAPIConfig
├── plugin.py        # AsyncAPIPlugin
├── plugins.py       # Render plugins
├── spec/            # Spec objects (PRD-001)
├── _asyncapi/       # Internal generation
└── extensions/      # Optional integrations
```

---

## Implementation Phases

### Phase 1: Spec Foundation (PRD-001)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md`
- Create ~20 spec object files
- BaseSchemaObject with serialization
- WebSocket bindings
- Full test coverage

### Phase 2: Schema Generation (PRD-002)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-002-schema-generation/prd.md`
- Type → Schema converters
- SchemaRegistry
- Pydantic/dataclass/msgspec support

### Phase 3: Handler Discovery (PRD-003)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-003-handler-discovery/prd.md`
- WebSocket extractor
- ChannelsPlugin extractor
- Operation mapping

### Phase 4: Document Generation (PRD-004)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-004-document-generation/prd.md`
- Generator orchestration
- Reference resolution
- Validation

### Phase 5: Render Plugins (PRD-005)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-005-render-plugins/prd.md`
- JSON/YAML plugins
- UI plugin (AsyncAPI Studio)
- Route registration

### Phase 6: Advanced Features (PRD-006)
**Status**: Not Started
**Docs**: `specs/active/asyncapi-plugin/prds/prd-006-advanced-features/prd.md`
- Traits support
- Custom decorators
- Additional bindings

---

## Quality Gates

Before marking any phase complete:

- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] 90%+ coverage for modified modules
- [ ] Pattern compliance verified
- [ ] No anti-patterns introduced

---

## References

### Specifications
- [AsyncAPI 3.0.0](https://www.asyncapi.com/docs/reference/specification/v3.0.0)
- [JSON Schema Draft 07](https://json-schema.org/specification-links.html#draft-7)

### Litestar Source (via gh API)
- `litestar/openapi/config.py` - Config pattern
- `litestar/openapi/plugins.py` - Plugin pattern
- `litestar/openapi/spec/` - Spec objects
- `litestar/_openapi/schema_generation/schema.py` - Schema gen

### External Examples
- [FastStream](https://github.com/ag2ai/faststream) - AsyncAPI generation
- [asyncapi-python](https://github.com/dutradda/asyncapi-python) - Spec handling

---

## Troubleshooting

### Common Issues

**Import errors in spec objects**:
- Do not use `from __future__ import annotations`
- Use `TYPE_CHECKING` for type-only imports and stringified annotations for forward refs

**Schema generation fails**:
- Check FieldDefinition handling
- Verify TYPE_MAP has required types

**Route registration fails**:
- Verify on_app_init() returns app_config
- Check route path conflicts

**Test failures**:
- Run `make test` with verbose flag
- Check fixture imports in conftest.py

---

## Next Agent Command

Start with the first sub-PRD:

- `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/prd.md`
- `specs/active/asyncapi-plugin/prds/prd-001-spec-foundation/tasks.md`
