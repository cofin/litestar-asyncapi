---
description: Explore and understand the codebase
allowed-tools: Read, Glob, Grep, Bash, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__sequential-thinking__sequentialthinking
---

# Codebase Exploration Workflow

You are exploring: **$ARGUMENTS**

This command helps understand the codebase structure, patterns, and conventions.

## Exploration Modes

Based on `$ARGUMENTS`:

| Argument | Mode | Description |
|----------|------|-------------|
| (empty) | Overview | Full codebase overview |
| `patterns` | Patterns | Document existing patterns |
| `[keyword]` | Search | Find specific functionality |
| `architecture` | Architecture | Deep dive into structure |

---

## Mode: Overview (no arguments)

### Step 1: Project Structure
```bash
tree -L 3 -I '__pycache__|*.pyc|.git|.venv|*.egg-info'
```

### Step 2: Core Components
```bash
cat src/litestar_asyncapi/__init__.py
```

### Step 3: Configuration
```bash
cat pyproject.toml | head -50
```

### Step 4: Key Files
```bash
wc -l src/litestar_asyncapi/*.py
```

### Step 5: Test Structure
```bash
ls -la src/tests/
wc -l src/tests/*.py
```

### Output Summary
```markdown
## Codebase Overview

### Structure
- Main package: src/litestar_asyncapi/
- Tests: src/tests/
- Specs: specs/

### Core Components
- AsyncAPIPlugin: Plugin class implementing InitPluginProtocol
- AsyncAPIConfig: Configuration dataclass

### Size
- Source files: [count]
- Total lines: [count]
- Test files: [count]

### Entry Points
- Public API: AsyncAPIPlugin, AsyncAPIConfig
```

---

## Mode: Patterns (`patterns`)

### Step 1: Read Pattern Library
```bash
cat specs/guides/patterns/README.md
```

### Step 2: Extract Live Patterns
```bash
# Plugin patterns
grep -A 20 "class.*Plugin" src/litestar_asyncapi/plugin.py

# Config patterns
grep -A 20 "@dataclass" src/litestar_asyncapi/config.py

# Test patterns
grep -A 10 "@pytest.fixture" src/tests/conftest.py
```

### Step 3: Document Patterns

For each pattern found:
1. Name and purpose
2. Code location
3. Usage example
4. Variations observed

### Output Summary
```markdown
## Patterns Found

### Plugin Pattern
- Location: src/litestar_asyncapi/plugin.py
- Type: InitPluginProtocol implementation
- Key features: __slots__, config property, on_app_init hook

### Config Pattern
- Location: src/litestar_asyncapi/config.py
- Type: Dataclass with defaults
- Key features: field descriptions as docstrings

### Test Pattern
- Location: src/tests/
- Type: Function-based with fixtures
- Key features: anyio marker, TYPE_CHECKING imports
```

---

## Mode: Search (`[keyword]`)

### Step 1: File Search
```bash
# Find files containing keyword
grep -rl "$ARGUMENTS" src/

# Find definitions
grep -rn "class.*$ARGUMENTS\|def.*$ARGUMENTS" src/
```

### Step 2: Usage Search
```bash
# Find usages
grep -rn "$ARGUMENTS" src/ --include="*.py"
```

### Step 3: Test Search
```bash
# Find related tests
grep -rn "$ARGUMENTS" src/tests/
```

### Step 4: Context Analysis

Use sequential thinking if complex:
```python
mcp__sequential-thinking__sequentialthinking(
    thought="Analyzing how $ARGUMENTS is used in the codebase...",
    thought_number=1,
    total_thoughts=8,
    next_thought_needed=True
)
```

### Output Summary
```markdown
## Search Results: $ARGUMENTS

### Definitions
- [file:line] - [definition]

### Usages
- [file:line] - [context]

### Tests
- [file:line] - [test name]

### Analysis
[Summary of how this component works]
```

---

## Mode: Architecture (`architecture`)

### Step 1: Read Architecture Guide
```bash
cat specs/guides/architecture.md
```

### Step 2: Component Analysis
```bash
# List all classes
grep -rn "^class " src/litestar_asyncapi/

# List all public functions
grep -rn "^def " src/litestar_asyncapi/ | grep -v "^def _"
```

### Step 3: Dependency Analysis
```bash
# Internal imports
grep -rn "from litestar_asyncapi" src/

# External imports
grep -rn "from litestar" src/litestar_asyncapi/
grep -rn "import " src/litestar_asyncapi/ | grep -v "from litestar_asyncapi"
```

### Step 4: Integration Points
```bash
# Litestar hooks
grep -rn "on_app_init\|InitPluginProtocol" src/
```

### Step 5: Deep Analysis

Use mcp__sequential-thinking for thorough analysis:
```python
mcp__sequential-thinking__sequentialthinking(
    thought="Step 1: Mapping the architectural components...",
    thought_number=1,
    total_thoughts=12,
    next_thought_needed=True
)
```

### Output Summary
```markdown
## Architecture Analysis

### Component Diagram
\`\`\`
Litestar App
    │
    ├── AsyncAPIPlugin (InitPluginProtocol)
    │       │
    │       └── AsyncAPIConfig
    │
    └── [Future: Schema Generation]
\`\`\`

### Dependencies
- External: litestar>=2.0.0, sniffio
- Internal: [component relationships]

### Integration Points
- on_app_init: App initialization hook
- [Future hooks]

### Extension Points
- Config customization
- [Future: Schema customizers]
```

---

## Litestar Documentation Lookup

If you need Litestar-specific information:

```python
# Resolve library ID
mcp__context7__resolve-library-id(libraryName="litestar")

# Get documentation
mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/litestar-org/litestar",
    topic="plugins",  # or: websocket, channels, routing, etc.
    mode="code"
)
```

---

## Output

Always end with a clear summary of what was found and any recommendations for next steps.
