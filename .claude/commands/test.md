---
description: Testing workflow with coverage targets
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, mcp__pal__debug
---

# Testing Workflow

You are running tests for: **$ARGUMENTS**

If `$ARGUMENTS` is a feature slug, load context from `specs/active/{slug}/`.
If `$ARGUMENTS` is empty, run project-wide tests.

## Critical Rules

1. **90%+ COVERAGE** - Modified modules must achieve 90%+ coverage
2. **FUNCTION-BASED** - Use function-based tests, not class-based
3. **ASYNC MARKERS** - Use `pytestmark = pytest.mark.anyio`
4. **PATTERN COMPLIANCE** - Follow test patterns from conftest.py
5. **ISOLATION** - Tests must work in parallel

---

## Checkpoint 1: Load Test Context

**If feature slug provided:**
```bash
cat specs/active/$ARGUMENTS/prd.md | grep -A 50 "Testing Strategy"
cat specs/active/$ARGUMENTS/tasks.md | grep -A 10 "Tests"
```

**Load test patterns:**
```bash
cat src/tests/conftest.py
cat specs/guides/patterns/README.md | grep -A 50 "Test"
```

**Output**: "Checkpoint 1 complete - Test context loaded"

---

## Checkpoint 2: Run Existing Tests

```bash
make test
```

**Expected**: All tests pass

**If tests fail:**
- Note failures
- Do NOT proceed until existing tests pass
- Use mcp__pal__debug if needed

**Output**: "Checkpoint 2 complete - Existing tests pass"

---

## Checkpoint 3: Coverage Analysis

```bash
uv run pytest src/tests --cov=src/litestar_asyncapi --cov-report=term-missing
```

**Identify:**
- Overall coverage percentage
- Uncovered lines in modified files
- Missing test scenarios

**Output**: "Checkpoint 3 complete - Coverage: [percentage]%"

---

## Checkpoint 4: Write Missing Tests

**For each uncovered code path:**

### Test Template
```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

pytestmark = pytest.mark.anyio


def test_[feature]_[scenario]() -> None:
    """Test that [what is being tested].

    Verifies [expected behavior].
    """
    # Arrange
    from litestar_asyncapi import SomeClass

    # Act
    result = SomeClass()

    # Assert
    assert result.field == expected_value
```

### Use Existing Fixtures
```python
def test_feature_with_app(app: "Litestar", asyncapi_plugin: "AsyncAPIPlugin") -> None:
    """Test feature with full app context."""
    assert asyncapi_plugin in app.plugins
```

**Output**: "Checkpoint 4 complete - [count] tests added"

---

## Checkpoint 5: Edge Cases

**Test edge cases:**

1. **None/Empty values**
```python
def test_config_with_none_description() -> None:
    config = AsyncAPIConfig(description=None)
    assert config.description is None
```

2. **Invalid inputs** (if applicable)
```python
def test_invalid_input_raises() -> None:
    with pytest.raises(ValueError, match="expected message"):
        SomeClass(invalid="value")
```

3. **Boundary conditions**
```python
def test_empty_servers_dict() -> None:
    config = AsyncAPIConfig(servers={})
    assert config.servers == {}
```

**Output**: "Checkpoint 5 complete - Edge cases covered"

---

## Checkpoint 6: Run Full Test Suite

```bash
make test
```

**Verify:**
- All tests pass
- No warnings (or only expected deprecation warnings)

**Output**: "Checkpoint 6 complete - All tests pass"

---

## Checkpoint 7: Verify Coverage Target

```bash
uv run pytest src/tests --cov=src/litestar_asyncapi --cov-report=term-missing --cov-fail-under=90
```

**Target**: 90%+ coverage for modified modules

**If below 90%:**
- Identify uncovered lines
- Add tests for those paths
- Re-run coverage check

**Output**: "Checkpoint 7 complete - Coverage: [percentage]% (target: 90%)"

---

## Checkpoint 8: Type Check Tests

```bash
uv run mypy src/tests/
uv run pyright src/tests/
```

**Verify:**
- No type errors in test files
- Proper TYPE_CHECKING imports

**Output**: "Checkpoint 8 complete - Tests type-check clean"

---

## Final Summary

```
Testing Phase Complete

Test Results:
- Total tests: [count]
- New tests: [count]
- All passing: YES

Coverage:
- Overall: [percentage]%
- Modified modules: [percentage]%
- Target (90%): [MET/NOT MET]

Quality:
- Type checking: PASS
- No warnings: [YES/NO]

Files Changed:
- src/tests/test_[name].py

Next: Run `/review {slug}` (if feature) or commit changes
```
