---
description: Quality gate and pattern extraction review
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, mcp__pal__analyze
---

# Review Workflow

You are reviewing: **$ARGUMENTS**

If `$ARGUMENTS` is a feature slug, review the full feature implementation.
If `$ARGUMENTS` is empty, review uncommitted changes.

## Critical Rules

1. **ALL GATES MUST PASS** - No exceptions
2. **PATTERN EXTRACTION** - Document new patterns found
3. **NO NEW CODE** - Review only, no implementation
4. **THOROUGH** - Check every changed file

---

## Checkpoint 1: Load Review Context

**If feature slug provided:**
```bash
cat specs/active/$ARGUMENTS/prd.md
cat specs/active/$ARGUMENTS/tasks.md
```

**Get changed files:**
```bash
git diff --name-only HEAD~1  # or appropriate ref
git status --porcelain
```

**Output**: "Checkpoint 1 complete - Context loaded, [count] files to review"

---

## Checkpoint 2: Quality Gate - Tests

```bash
make test
```

**Requirement**: ALL tests must pass

**If failing:**
- List failing tests
- STOP review
- Implementation must fix tests first

**Output**: "Checkpoint 2 complete - Tests: PASS"

---

## Checkpoint 3: Quality Gate - Linting

```bash
make lint
```

This runs:
- pre-commit hooks
- mypy type checking
- pyright type checking
- slotscheck

**Requirement**: Zero errors

**If failing:**
- List errors
- STOP review
- Implementation must fix lint errors first

**Output**: "Checkpoint 3 complete - Lint: PASS"

---

## Checkpoint 4: Quality Gate - Coverage

```bash
uv run pytest src/tests --cov=src/litestar_asyncapi --cov-report=term-missing --cov-fail-under=90
```

**Requirement**: 90%+ coverage for modified modules

**If below threshold:**
- List uncovered lines
- STOP review
- Implementation must add tests first

**Output**: "Checkpoint 4 complete - Coverage: [percentage]% (PASS)"

---

## Checkpoint 5: Code Quality Analysis

**Use mcp__pal__analyze for thorough review:**

```python
mcp__pal__analyze(
    step="Analyze code quality for feature implementation",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="Reviewing code patterns, architecture, and quality...",
    analysis_type="quality",
    relevant_files=["/path/to/changed/files"]
)
```

**Check for:**

### Style Compliance
- [ ] No `from __future__ import annotations`
- [ ] PEP 604 types (`T | None` not `Optional[T]`)
- [ ] Google-style docstrings
- [ ] Absolute imports only
- [ ] `__slots__` on classes

### Pattern Compliance
- [ ] Follows InitPluginProtocol pattern
- [ ] Configuration uses dataclass pattern
- [ ] Tests use function-based pattern
- [ ] Fixtures follow conftest.py patterns

### Code Quality
- [ ] No code duplication
- [ ] Functions are focused (single responsibility)
- [ ] Error handling is appropriate
- [ ] No hardcoded values that should be config

**Output**: "Checkpoint 5 complete - Code quality: [PASS/ISSUES FOUND]"

---

## Checkpoint 6: Anti-Pattern Scan

**Check for banned patterns:**

```bash
# Check for Optional import
grep -r "from typing import.*Optional" src/ && echo "FAIL: Optional import found"

# Check for Optional usage
grep -r "Optional\[" src/ && echo "FAIL: Optional[] usage found"

# Check for relative imports
grep -r "from \.\." src/litestar_asyncapi/ && echo "FAIL: Relative imports found"

# Check for future annotations import (disallowed)
grep -r "from __future__ import annotations" src/litestar_asyncapi/ && echo "FAIL: Future annotations import found"
```

**Requirement**: No banned patterns

**Output**: "Checkpoint 6 complete - Anti-patterns: NONE FOUND"

---

## Checkpoint 7: Documentation Review

**Check documentation:**

- [ ] New public APIs have docstrings
- [ ] Docstrings follow Google style
- [ ] Complex logic has inline comments
- [ ] README updated if needed (public API changes)

**Output**: "Checkpoint 7 complete - Documentation: ADEQUATE"

---

## Checkpoint 8: Pattern Extraction

**If new patterns were discovered:**

1. Read `specs/active/{slug}/tmp/new-patterns.md` (if exists)
2. Evaluate if pattern is reusable
3. Extract to `specs/guides/patterns/`

**Pattern extraction format:**
```markdown
# Pattern: [Name]

## When to Use
[Describe when this pattern applies]

## Implementation
\`\`\`python
[Code example]
\`\`\`

## Example Usage
[Where this is used in codebase]

## Testing
[How to test this pattern]
```

**Output**: "Checkpoint 8 complete - Patterns extracted: [count]"

---

## Checkpoint 9: Archive Feature Workspace

**If all gates pass and feature is complete:**

```bash
mv specs/active/{slug} specs/archive/{slug}-$(date +%Y%m%d)
```

**Update archive with completion status:**
```markdown
# Completion Summary

- Completed: [date]
- Final coverage: [percentage]%
- Tasks completed: [count]/[total]
- Patterns extracted: [count]
```

**Output**: "Checkpoint 9 complete - Feature archived"

---

## Final Summary

```
Review Phase Complete

Feature: {slug}
Status: [APPROVED / NEEDS WORK]

Quality Gates:
- Tests: [PASS/FAIL]
- Lint: [PASS/FAIL]
- Coverage: [percentage]% [PASS/FAIL]
- Anti-patterns: [NONE/FOUND]

Code Quality:
- Style compliance: [PASS/FAIL]
- Pattern compliance: [PASS/FAIL]
- Documentation: [ADEQUATE/NEEDS WORK]

Patterns Extracted: [count]
- [list if any]

Workspace: [archived location or still active]

[If APPROVED]
Ready for commit. Suggested commit message:

feat: [feature description]

- [change 1]
- [change 2]

[If NEEDS WORK]
Issues to address:
- [issue 1]
- [issue 2]

Re-run `/review {slug}` after fixes.
```
