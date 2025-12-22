---
description: Create a PRD with pattern learning and adaptive complexity
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__sequential-thinking__sequentialthinking, mcp__pal__planner
---

# Intelligent PRD Creation Workflow

You are creating a Product Requirements Document for: **$ARGUMENTS**

## Intelligence Layer (ACTIVATE FIRST)

Before starting checkpoints:

1. **Read MCP Strategy**: Load `.claude/mcp-strategy.md` for tool selection
2. **Learn from Codebase**: Read 3-5 similar implementations
3. **Assess Complexity**: Determine simple/medium/complex
4. **Adapt Workflow**: Adjust checkpoint depth

## Critical Rules

1. **CONTEXT FIRST** - Read existing patterns before planning
2. **NO CODE MODIFICATION** - Planning only (specs/ directory only)
3. **PATTERN LEARNING** - Identify 3-5 similar features
4. **ADAPTIVE DEPTH** - Simple=6, Medium=8, Complex=10+ checkpoints
5. **RESEARCH GROUNDED** - Minimum 2000+ words research
6. **COMPREHENSIVE PRD** - Minimum 3200+ words

---

## Checkpoint 0: Intelligence Bootstrap

**Load project intelligence:**

```bash
# Read key files
cat CLAUDE.md
cat specs/guides/architecture.md
cat specs/guides/patterns/README.md
cat .claude/mcp-strategy.md
```

**Learn from existing implementations:**

```bash
# Find similar features in codebase
grep -r "class.*{keyword}" src/ | head -5
```

**Assess complexity:**

| Level | Criteria | Checkpoints |
|-------|----------|-------------|
| Simple | Single file, CRUD, config change | 6 |
| Medium | New service, 2-3 files, API endpoint | 8 |
| Complex | Architecture change, 5+ files, new subsystem | 10+ |

**Output**: "Checkpoint 0 complete - Complexity: [level], Checkpoints: [count]"

---

## Checkpoint 1: Pattern Recognition

**Identify similar implementations:**

1. Search for related patterns in `src/litestar_asyncapi/`
2. Read at least 3 similar files if they exist
3. Check `specs/guides/patterns/` for documented patterns
4. Note testing patterns from `src/tests/`

**Document in workspace:**

```markdown
## Similar Implementations

1. `src/path/to/similar1.py` - Description
2. `src/path/to/similar2.py` - Description

## Patterns Observed

- Class structure: InitPluginProtocol pattern
- Naming conventions: snake_case for functions, PascalCase for classes
- Error handling: Raise custom exceptions
```

**Output**: "Checkpoint 1 complete - Patterns identified"

---

## Checkpoint 2: Workspace Creation

Create the feature workspace:

```bash
mkdir -p specs/active/{slug}/research
mkdir -p specs/active/{slug}/tmp
mkdir -p specs/active/{slug}/patterns
```

Where `{slug}` is derived from the feature name (lowercase, hyphens).

**Output**: "Checkpoint 2 complete - Workspace at specs/active/{slug}/"

---

## Checkpoint 3: Intelligent Analysis

**Choose tool based on complexity:**

| Complexity | Tool | Configuration |
|------------|------|---------------|
| Simple | Manual analysis | 5-7 thoughts |
| Medium | sequential_thinking | 12 thoughts |
| Complex | mcp__pal__planner | 4-6 steps |

**For Litestar plugin features, analyze:**

1. How does this fit with InitPluginProtocol?
2. What Litestar APIs will be used?
3. What AsyncAPI spec sections are involved?
4. Testing approach and fixtures needed

**Output**: "Checkpoint 3 complete - Analysis using [tool]"

---

## Checkpoint 4: Research (2000+ words)

**Priority order for research:**

1. **Pattern Library**: `specs/guides/patterns/`
2. **Internal Guides**: `specs/guides/architecture.md`
3. **Context7**: Litestar documentation
   ```
   mcp__context7__resolve-library-id(libraryName="litestar")
   mcp__context7__get-library-docs(context7CompatibleLibraryID="/litestar-org/litestar", topic="plugins")
   ```
4. **WebSearch**: AsyncAPI specification, best practices

**Write research to**: `specs/active/{slug}/research/plan.md`

**Verify word count:**
```bash
wc -w specs/active/{slug}/research/plan.md
```

**Output**: "Checkpoint 4 complete - Research ([word count] words)"

---

## Checkpoint 5: Write PRD (3200+ words)

Create `specs/active/{slug}/prd.md` with:

### Required Sections

1. **Intelligence Context**
   - Complexity assessment
   - Similar features identified
   - Patterns to follow

2. **Problem Statement**
   - What problem does this solve?
   - Who benefits?

3. **Acceptance Criteria**
   - Specific, measurable criteria
   - Edge cases covered

4. **Technical Approach**
   - Implementation strategy
   - Pattern references
   - Litestar integration points

5. **Testing Strategy**
   - Unit test approach
   - Integration test approach
   - Coverage requirements (90%+)

6. **File Changes**
   - Files to create
   - Files to modify
   - Estimated lines of code

**Verify word count:**
```bash
wc -w specs/active/{slug}/prd.md
```

**Output**: "Checkpoint 5 complete - PRD ([word count] words)"

---

## Checkpoint 6: Task Breakdown

Create `specs/active/{slug}/tasks.md`:

**Adapt task granularity to complexity:**

| Complexity | Tasks | Detail Level |
|------------|-------|--------------|
| Simple | 4-6 | High-level |
| Medium | 6-10 | Medium |
| Complex | 10-15 | Detailed |

**Task format:**
```markdown
## Task 1: [Title]
- **Files**: list of files
- **Changes**: what to implement
- **Tests**: what tests to add
- **Patterns**: patterns to follow
```

**Output**: "Checkpoint 6 complete - [count] tasks created"

---

## Checkpoint 7: Recovery Guide

Create `specs/active/{slug}/recovery.md`:

```markdown
# Recovery Guide: {feature}

## Session Context
- Complexity: [level]
- Checkpoints: [count]
- Created: [date]

## Quick Resume
1. Read this file
2. Read prd.md
3. Check tasks.md for progress
4. Continue from last incomplete task

## Intelligence Context
- Similar features: [list]
- Patterns used: [list]
- MCP tools needed: [list]

## File Locations
- PRD: specs/active/{slug}/prd.md
- Tasks: specs/active/{slug}/tasks.md
- Research: specs/active/{slug}/research/

## Next Agent
Run: `/implement {slug}`
```

**Output**: "Checkpoint 7 complete - Recovery guide created"

---

## Checkpoint 8: Git Verification

Verify no source code was modified:

```bash
git status --porcelain src/ | grep -v "^??"
```

**Expected**: Empty output (no source changes)

**Output**: "Checkpoint 8 complete - No source code modified"

---

## Final Summary

```
PRD Phase Complete

Workspace: specs/active/{slug}/
Complexity: [simple|medium|complex]
Checkpoints: [count] completed

Intelligence:
- Pattern library consulted
- [count] similar features analyzed
- Tool selection optimized

Files Created:
- specs/active/{slug}/prd.md ([word count] words)
- specs/active/{slug}/tasks.md ([task count] tasks)
- specs/active/{slug}/research/plan.md ([word count] words)
- specs/active/{slug}/recovery.md

Next: Run `/implement {slug}`
```
