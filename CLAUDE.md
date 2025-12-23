# AI Agent Guidelines for litestar-asyncapi

**Version**: 2.0 (Intelligent Edition) | **Updated**: 2025-12-16

This is **litestar-asyncapi**, an official Litestar plugin that provides AsyncAPI support. AsyncAPI is a specification similar to OpenAPI but designed for event-driven/asynchronous APIs (WebSockets, message brokers, etc.).

---

## Intelligence Layer

This project uses an **intelligent agent system** that:

1. **Learns from codebase** before making changes
2. **Adapts workflow depth** based on feature complexity
3. **Accumulates knowledge** in pattern library
4. **Selects tools** based on task requirements

### Pattern Library

Reusable patterns in `specs/guides/patterns/`:

- Consult before implementing similar features
- Add new patterns during review phase

### Complexity-Based Checkpoints

| Complexity | Checkpoints | Triggers |
|------------|-------------|----------|
| Simple | 6 | CRUD, config change, single file |
| Medium | 8 | New service, API endpoint, 2-3 files |
| Complex | 10+ | Architecture change, multi-component |

---

## Quick Reference

### Technology Stack

| Category | Tool |
|----------|------|
| Framework | Litestar 2.0+ |
| Testing | pytest + anyio |
| Linting | ruff |
| Type Checking | mypy + pyright |
| Package Manager | uv |
| Build Backend | hatchling |

### Essential Commands

```bash
make install       # Install all dependencies
make test          # Run all tests
make lint          # Run linting (pre-commit + type-check + slotscheck)
make fix           # Auto-format code
make check-all     # Run all checks (lint + test + coverage)
make coverage      # Run tests with coverage report
```

---

## Code Standards (Critical)

### Python

| Rule | Standard |
|------|----------|
| Type hints | PEP 604 (`T \| None`, NOT `Optional[T]`) |
| Future imports | Do **not** use `from __future__ import annotations` |
| Docstrings | Google style |
| Tests | Function-based, `pytest.mark.anyio` |
| Line length | 120 characters |
| Imports | Absolute only (relative imports banned) |
| Classes | Must define `__slots__` |

### Required File Header

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type-only imports here
    pass
```

### Typing Notes

- Use stringified annotations (e.g. `"Litestar"` / `"AsyncAPIGenerator"`) when referencing types that are only imported
  under `TYPE_CHECKING`.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/prd [feature]` | Create PRD with pattern learning |
| `/implement [slug]` | Pattern-guided implementation |
| `/test [slug]` | Testing with 90%+ coverage |
| `/review [slug]` | Quality gate and pattern extraction |
| `/explore [topic]` | Explore codebase |
| `/fix-issue [#]` | Fix GitHub issue |
| `/bootstrap` | Re-bootstrap (alignment mode) |

---

## Subagents

| Agent | Mission |
|-------|---------|
| `prd` | PRD creation with pattern recognition |
| `expert` | Implementation with pattern compliance |
| `testing` | Test creation (90%+ coverage) |
| `docs-vision` | Quality gates and pattern extraction |

---

## Project Structure

```
src/litestar_asyncapi/
├── __init__.py      # Public exports
├── config.py        # AsyncAPIConfig dataclass
├── plugin.py        # AsyncAPIPlugin (InitPluginProtocol)
└── py.typed         # PEP 561 marker

src/tests/
├── conftest.py      # Test fixtures
└── test_plugin.py   # Plugin tests

specs/
├── guides/
│   ├── architecture.md    # Architecture overview
│   ├── patterns/          # Pattern library
│   └── quality-gates.yaml # Quality gate definitions
├── active/                # Active feature workspaces
└── archive/               # Completed features

.claude/
├── commands/        # Slash commands
├── agents/          # Subagent definitions
├── skills/          # Framework skills
└── mcp-strategy.md  # MCP tool selection guide
```

---

## Development Workflow

### For New Features (Pattern-First)

1. **PRD**: `/prd [feature]` - Analyzes similar features first
2. **Implement**: `/implement [slug]` - Follows identified patterns
3. **Test**: Auto-invoked - Tests pattern compliance
4. **Review**: Auto-invoked - Extracts new patterns to library

### Quality Gates

All code must pass:

- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] 90%+ coverage for modified modules
- [ ] Pattern compliance verified
- [ ] No anti-patterns

---

## MCP Tools

### Tool Selection Guide

See `.claude/mcp-strategy.md` for detailed tool selection.

### Context7 (Litestar Docs)

```python
mcp__context7__resolve-library-id(libraryName="litestar")
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="plugins",  # or: websocket, routing, testing
    mode="code"
)
```

### Sequential Thinking (Analysis)

```python
mcp__sequential-thinking__sequentialthinking(
    thought="Step 1: Analyze the plugin structure...",
    thought_number=1,
    total_thoughts=12,
    next_thought_needed=True
)
```

### Pal Tools

- `mcp__pal__planner` - Multi-phase planning
- `mcp__pal__thinkdeep` - Deep analysis
- `mcp__pal__analyze` - Code analysis
- `mcp__pal__debug` - Debugging

---

## Anti-Patterns (Must Avoid)

| Pattern | Issue | Fix |
|---------|-------|-----|
| `Optional[T]` | Old style | Use `T \| None` |
| `from typing import Optional` | Unnecessary | Remove import |
| `from ..` | Relative import | Use absolute import |
| Missing `__slots__` | Memory waste | Add `__slots__` to classes |
| Class-based tests | Not preferred | Use function-based tests |
| `from __future__ import annotations` | Disallowed | Remove it; use stringified annotations + `TYPE_CHECKING` imports |

---

## Architecture

The plugin follows the standard Litestar plugin pattern:

```
Litestar App
    │
    ├── AsyncAPIPlugin (InitPluginProtocol)
    │       │
    │       └── AsyncAPIConfig
    │
    └── [Future: Schema Generation, UI, Routes]
```

### Integration Points

- `on_app_init()` - App initialization hook
- Routes added via `app_config.route_handlers`
- Middleware via `app_config.middleware`

---

## Testing

### Test Pattern

```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

pytestmark = pytest.mark.anyio


def test_feature(app: "Litestar", asyncapi_config: "AsyncAPIConfig") -> None:
    """Test description."""
    from litestar_asyncapi import SomeClass

    result = SomeClass()
    assert result.field == expected
```

### Available Fixtures (conftest.py)

- `anyio_backend` - Returns "asyncio"
- `asyncapi_config` - Test configuration
- `asyncapi_plugin` - Plugin instance
- `app` - Litestar app with plugin

---

## Resources

- **Litestar Docs**: <https://docs.litestar.dev/>
- **AsyncAPI Spec**: <https://www.asyncapi.com/docs/reference/specification>
- **Pattern Library**: `specs/guides/patterns/`
- **Architecture Guide**: `specs/guides/architecture.md`
