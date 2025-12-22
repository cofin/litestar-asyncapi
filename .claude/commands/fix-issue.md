---
description: Fix a GitHub issue with pattern compliance
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, mcp__pal__debug, mcp__pal__thinkdeep
---

# GitHub Issue Fix Workflow

You are fixing issue: **$ARGUMENTS**

`$ARGUMENTS` should be a GitHub issue number (e.g., `42` or `#42`).

## Critical Rules

1. **UNDERSTAND FIRST** - Read and analyze the issue thoroughly
2. **PATTERN COMPLIANCE** - Follow project patterns
3. **TEST COVERAGE** - Add tests for the fix
4. **QUALITY GATES** - All checks must pass
5. **MINIMAL CHANGES** - Fix only what's needed

---

## Checkpoint 1: Fetch Issue Details

```bash
# Get issue details
gh issue view $ARGUMENTS --json title,body,labels,comments
```

**Extract:**
- Issue title and description
- Reproduction steps (if bug)
- Expected behavior
- Labels (bug, feature, etc.)

**Output**: "Checkpoint 1 complete - Issue: [title]"

---

## Checkpoint 2: Issue Analysis

**Classify the issue:**

| Type | Approach |
|------|----------|
| Bug | Debug → Fix → Test |
| Feature | Mini-PRD → Implement → Test |
| Docs | Update docs → Verify |
| Refactor | Analyze impact → Change → Test |

**For bugs, use mcp__pal__debug:**
```python
mcp__pal__debug(
    step="Investigate issue #$ARGUMENTS: [title]",
    step_number=1,
    total_steps=4,
    next_step_required=True,
    findings="Initial analysis...",
    hypothesis="Possible cause..."
)
```

**Output**: "Checkpoint 2 complete - Type: [bug/feature/docs/refactor]"

---

## Checkpoint 3: Locate Relevant Code

```bash
# Search for related code
grep -rn "[keyword from issue]" src/

# Find potentially affected files
git log --oneline --all -- "src/**/*[related]*"
```

**Read relevant files:**
- Main implementation files
- Related test files
- Configuration if applicable

**Output**: "Checkpoint 3 complete - [count] relevant files identified"

---

## Checkpoint 4: Create Fix Workspace

```bash
mkdir -p specs/active/issue-$ARGUMENTS/tmp
```

**Document analysis:**
```markdown
# Issue #$ARGUMENTS Fix

## Issue Summary
[Brief description]

## Root Cause
[Analysis of why this happens]

## Proposed Fix
[Description of the fix]

## Files to Change
- [file1] - [change description]
- [file2] - [change description]

## Tests to Add
- [test description]
```

Save to: `specs/active/issue-$ARGUMENTS/analysis.md`

**Output**: "Checkpoint 4 complete - Workspace created"

---

## Checkpoint 5: Implement Fix

**Follow project patterns:**

1. Read similar code for patterns
2. Make minimal, focused changes
3. Use proper type hints
4. Add docstrings where needed

**Style requirements:**
- Do not use `from __future__ import annotations`
- PEP 604 types (`T | None`)
- Google-style docstrings
- Absolute imports

**Output**: "Checkpoint 5 complete - Fix implemented"

---

## Checkpoint 6: Add Tests

**Test the fix:**

```python
	import pytest

pytestmark = pytest.mark.anyio


def test_issue_$ARGUMENTS_[scenario]() -> None:
    """Test that [issue description] is fixed.

    Regression test for issue #$ARGUMENTS.
    """
    # Arrange - set up the scenario from the issue

    # Act - perform the action that triggered the bug

    # Assert - verify the fix works
```

**Test file location:**
- If existing test file covers this area, add there
- Otherwise, create focused test file

**Output**: "Checkpoint 6 complete - Tests added"

---

## Checkpoint 7: Run Quality Gates

```bash
make test
make lint
```

**All must pass.**

**If failing:**
- Fix issues
- Re-run checks
- Document any unexpected complications

**Output**: "Checkpoint 7 complete - Quality gates: PASS"

---

## Checkpoint 8: Verify Coverage

```bash
uv run pytest src/tests --cov=src/litestar_asyncapi --cov-report=term-missing
```

**Ensure:**
- New code is covered by tests
- No decrease in overall coverage
- Fix-specific tests cover the scenario

**Output**: "Checkpoint 8 complete - Coverage verified"

---

## Checkpoint 9: Prepare Commit

**Generate commit message:**

```markdown
fix: [brief description] (#$ARGUMENTS)

[Longer description if needed]

Fixes #$ARGUMENTS
```

**Verify changes:**
```bash
git diff --stat
git diff src/
```

**Output**: "Checkpoint 9 complete - Ready for commit"

---

## Checkpoint 10: Clean Up

```bash
# Archive workspace
mv specs/active/issue-$ARGUMENTS specs/archive/issue-$ARGUMENTS-$(date +%Y%m%d)
```

**Output**: "Checkpoint 10 complete - Workspace archived"

---

## Final Summary

```
Issue Fix Complete

Issue: #$ARGUMENTS - [title]
Type: [bug/feature/docs/refactor]
Status: FIXED

Changes:
- [file1]: [description]
- [file2]: [description]

Tests Added:
- test_issue_$ARGUMENTS_[scenario]

Quality:
- Tests: PASS
- Lint: PASS
- Coverage: [percentage]%

Commit Message:
fix: [description] (#$ARGUMENTS)

[description]

Fixes #$ARGUMENTS

Next Steps:
1. Review changes: git diff
2. Commit: git commit
3. Push: git push
4. Close issue with PR
```
