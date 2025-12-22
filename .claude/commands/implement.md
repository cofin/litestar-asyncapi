---
description: Pattern-guided implementation of a PRD
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__pal__thinkdeep, mcp__pal__debug
---

# Pattern-Guided Implementation Workflow

You are implementing the feature: **$ARGUMENTS**

## Pre-Implementation Setup

**Load context:**

```bash
# Load PRD and patterns
cat specs/active/$ARGUMENTS/prd.md
cat specs/active/$ARGUMENTS/tasks.md
cat specs/active/$ARGUMENTS/recovery.md
cat specs/guides/patterns/README.md
```

## Critical Rules

1. **PATTERN COMPLIANCE** - Follow patterns from similar features
2. **TASK-BY-TASK** - Complete one task fully before moving to next
3. **TEST ALONGSIDE** - Write tests as you implement
4. **QUALITY GATES** - Run `make lint` and `make test` after each task
5. **DOCUMENT PATTERNS** - Note new patterns in `tmp/new-patterns.md`

---

## Checkpoint 1: Load Intelligence Context

**Read all context files:**

1. `specs/active/{slug}/prd.md` - Requirements
2. `specs/active/{slug}/tasks.md` - Task breakdown
3. `specs/active/{slug}/patterns/analysis.md` - Pattern analysis (if exists)
4. `specs/guides/patterns/README.md` - Project patterns

**Extract:**

- Similar implementations to reference
- Patterns to follow
- Files to modify

**Output**: "Checkpoint 1 complete - Context loaded"

---

## Checkpoint 2: Pattern Deep Dive

**Read 3-5 similar implementations:**

For each similar file identified in PRD:

1. Read the full file
2. Note class structure
3. Note naming conventions
4. Note error handling
5. Note docstring style

**Document patterns in**: `specs/active/{slug}/tmp/patterns-used.md`

**Output**: "Checkpoint 2 complete - Patterns documented"

---

## Checkpoint 3-N: Task Implementation

**For each task in tasks.md:**

### 3a. Pre-Task Check

```bash
# Verify clean state
make test
make lint
```

### 3b. Implement Task

- Follow identified patterns
- Use proper type hints (`T | None`, not `Optional[T]`)
- Do not add `from __future__ import annotations`; use string-literal type hints where needed
- Use `__slots__` for classes
- Write Google-style docstrings

### 3c. Write Tests

- Function-based tests (not class-based)
- Use `pytestmark = pytest.mark.anyio`
- 90%+ coverage for new code

### 3d. Post-Task Verify

```bash
make test
make lint
```

### 3e. Mark Task Complete

Update `specs/active/{slug}/tasks.md`:

```markdown
## Task N: [Title]
- **Status**: COMPLETE
- **Files Changed**: [list]
- **Tests Added**: [list]
```

**Output**: "Checkpoint [N] complete - Task [name] implemented"

---

## Checkpoint N+1: Document New Patterns

If you discovered new patterns during implementation:

**Create/update**: `specs/active/{slug}/tmp/new-patterns.md`

```markdown
# New Patterns Discovered

## Pattern: [Name]

### Context
When to use this pattern.

### Implementation
\`\`\`python
# Code example
\`\`\`

### Testing
How to test this pattern.
```

**Output**: "Checkpoint [N+1] complete - New patterns documented"

---

## Checkpoint N+2: Final Quality Gate

**Run all checks:**

```bash
make check-all
```

This runs:

- `make lint` (pre-commit + type-check + slotscheck)
- `make test`
- `make coverage`

**All must pass before proceeding.**

**Output**: "Checkpoint [N+2] complete - All quality gates passed"

---

## Checkpoint N+3: Update Recovery Guide

Update `specs/active/{slug}/recovery.md`:

```markdown
## Implementation Status
- Status: COMPLETE
- Tasks completed: [count]/[total]
- Coverage: [percentage]%

## Files Changed
- [list of files with brief description]

## Next Agent
Run: `/review {slug}`
```

**Output**: "Checkpoint [N+3] complete - Recovery guide updated"

---

## Auto-Invoke Testing Agent

After implementation is complete, invoke testing agent:

```
Task(
    subagent_type="testing",
    prompt="Run comprehensive tests for feature {slug}. PRD at specs/active/{slug}/prd.md"
)
```

---

## Final Summary

```
Implementation Phase Complete

Feature: {slug}
Tasks: [completed]/[total]

Quality:
- make test: PASS
- make lint: PASS
- Coverage: [percentage]%

Files Changed:
- [list]

Patterns:
- Followed: [list]
- New: [list or "None"]

Next: Review will run automatically, or run `/review {slug}`
```
