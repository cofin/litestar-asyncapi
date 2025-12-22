# MCP Tool Strategy

## Tool Selection by Task Type

### Complex Architectural Decisions
1. **Primary**: mcp__pal__thinkdeep
2. **Fallback**: mcp__sequential-thinking__sequentialthinking

### Library Documentation Lookup
1. **Primary**: mcp__context7__get-library-docs
2. **Fallback**: WebSearch

### Multi-Phase Planning
1. **Primary**: mcp__pal__planner
2. **Fallback**: Manual structured thinking

### Code Analysis
1. **Primary**: mcp__pal__analyze
2. **Fallback**: Manual code review

### Debugging
1. **Primary**: mcp__pal__debug
2. **Fallback**: Manual investigation

## Complexity-Based Selection

### Simple Features (6 checkpoints)
- Use basic tools
- Manual analysis acceptable
- Focus on speed

### Medium Features (8 checkpoints)
- Use sequential_thinking (12 steps)
- Include pattern analysis
- Moderate depth

### Complex Features (10+ checkpoints)
- Use zen_thinkdeep or zen_planner
- Deep pattern analysis
- Comprehensive research

## Context7 Quick Reference

### Litestar Documentation
```
mcp__context7__resolve-library-id(libraryName="litestar")
# Returns: /litestar-org/litestar

mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="plugins",
    mode="code"
)
```

### AsyncAPI Specification
```
# Use WebSearch for AsyncAPI spec as it may not be in Context7
WebSearch(query="AsyncAPI 3.0 specification")
```

## Sequential Thinking Usage

For medium-complexity analysis:
```
mcp__sequential-thinking__sequentialthinking(
    thought="Step 1: Analyze the current plugin structure...",
    thought_number=1,
    total_thoughts=12,
    next_thought_needed=True
)
```

## Pal Tools Usage

### For Architecture Decisions
```
mcp__pal__thinkdeep(
    step="Analyze AsyncAPI schema generation approach",
    step_number=1,
    total_steps=5,
    next_step_required=True,
    findings="..."
)
```

### For Planning Complex Features
```
mcp__pal__planner(
    step="Plan WebSocket channel documentation feature",
    step_number=1,
    total_steps=4,
    next_step_required=True
)
```

### For Debugging
```
mcp__pal__debug(
    step="Investigate schema generation failure",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="..."
)
```
