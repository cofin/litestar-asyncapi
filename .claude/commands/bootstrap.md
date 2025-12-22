---
description: Re-bootstrap or update AI infrastructure (alignment mode)
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Bootstrap Alignment Workflow

You are running bootstrap in **alignment mode** to update existing AI infrastructure.

## Alignment Mode Detection

This mode activates when:
- `.claude/commands/` directory exists
- `CLAUDE.md` file exists
- `specs/guides/` directory exists

## Critical Rules

1. **PRESERVE CUSTOM CONTENT** - Don't overwrite user customizations
2. **ADD MISSING** - Only add components that don't exist
3. **UPDATE VERSIONS** - Update templates to latest versions
4. **REPORT CHANGES** - Document what was changed

---

## Checkpoint 1: Inventory Existing Configuration

```bash
# List existing commands
echo "=== Commands ==="
ls .claude/commands/*.md 2>/dev/null || echo "None"

# List existing agents
echo "=== Agents ==="
ls .claude/agents/*.md 2>/dev/null || echo "None"

# List existing skills
echo "=== Skills ==="
ls -d .claude/skills/*/ 2>/dev/null || echo "None"

# Check CLAUDE.md
echo "=== CLAUDE.md ==="
head -5 CLAUDE.md 2>/dev/null | grep -i "version\|updated"

# Check pattern library
echo "=== Patterns ==="
ls specs/guides/patterns/*.md 2>/dev/null || echo "None"

# Check quality gates
echo "=== Quality Gates ==="
test -f specs/guides/quality-gates.yaml && echo "Exists" || echo "Missing"
```

**Output**: "Checkpoint 1 complete - Inventory taken"

---

## Checkpoint 2: Identify Missing Components

**Core commands (must exist):**
- [ ] prd.md
- [ ] implement.md
- [ ] test.md
- [ ] review.md
- [ ] explore.md
- [ ] fix-issue.md
- [ ] bootstrap.md

**Core agents (must exist):**
- [ ] prd.md
- [ ] expert.md
- [ ] testing.md
- [ ] docs-vision.md

**Infrastructure (must exist):**
- [ ] specs/guides/patterns/README.md
- [ ] specs/guides/quality-gates.yaml
- [ ] specs/guides/architecture.md
- [ ] .claude/mcp-strategy.md

**Create list of missing items.**

**Output**: "Checkpoint 2 complete - [count] components missing"

---

## Checkpoint 3: Check for Custom Content

**For each existing file, check for customizations:**

```bash
# Example: Check if command has custom sections
for cmd in .claude/commands/*.md; do
    if grep -q "## Custom\|## Project-Specific" "$cmd"; then
        echo "CUSTOM: $cmd"
    fi
done
```

**Document custom content locations for preservation.**

**Output**: "Checkpoint 3 complete - Custom content identified"

---

## Checkpoint 4: Generate Missing Components

**Only create files that don't exist:**

```bash
# Check and create missing directories
test -d specs/guides/patterns || mkdir -p specs/guides/patterns
test -d specs/active || mkdir -p specs/active
test -d specs/archive || mkdir -p specs/archive
test -d .claude/agents || mkdir -p .claude/agents
test -d .claude/skills/litestar || mkdir -p .claude/skills/litestar
```

**For each missing component, generate using current templates.**

**Output**: "Checkpoint 4 complete - [count] components created"

---

## Checkpoint 5: Update Existing Components

**For components that exist but may be outdated:**

1. Read existing file
2. Identify version/date markers
3. Compare with current template
4. If older, offer to update (preserving custom sections)

**Update strategy:**
- Keep user's custom sections intact
- Update boilerplate sections
- Add new sections from templates

**Output**: "Checkpoint 5 complete - [count] components updated"

---

## Checkpoint 6: Verify Infrastructure

```bash
# Verify all expected files exist
echo "=== Verification ==="
test -f CLAUDE.md && echo "CLAUDE.md" || echo "MISSING: CLAUDE.md"
test -d .claude/commands && echo ".claude/commands/" || echo "MISSING: .claude/commands/"
test -d .claude/agents && echo ".claude/agents/" || echo "MISSING: .claude/agents/"
test -d .claude/skills && echo ".claude/skills/" || echo "MISSING: .claude/skills/"
test -f .claude/settings.local.json && echo "settings.local.json" || echo "MISSING: settings.local.json"
test -d specs/guides && echo "specs/guides/" || echo "MISSING: specs/guides/"
test -d specs/guides/patterns && echo "specs/guides/patterns/" || echo "MISSING: specs/guides/patterns/"
test -f specs/guides/quality-gates.yaml && echo "quality-gates.yaml" || echo "MISSING: quality-gates.yaml"
```

**Output**: "Checkpoint 6 complete - Infrastructure verified"

---

## Final Summary

```
Bootstrap Alignment Complete

Mode: Alignment (updating existing infrastructure)

Inventory:
- Commands: [existing count]/7 core
- Agents: [existing count]/4 core
- Skills: [existing count]
- Infrastructure: [existing count]/4 core

Changes Made:

Created:
- [list of newly created files]

Updated:
- [list of updated files]

Preserved:
- [list of files with custom content preserved]

No Changes Needed:
- [list of files already up to date]

Verification: [PASS/FAIL]

Next Steps:
1. Review created/updated files
2. Run `/explore` to verify configuration
3. Start development with `/prd [feature]`
```
