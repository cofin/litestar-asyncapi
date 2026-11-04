---
type: Guide
title: Bash Style Guide
description: Shell scripting standards for automation, CI, and tools.
tags: [styleguide, bash, shell]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
---

# Bash & Shell Scripting Guide

Based on Google Shell Style Guide principles for portable, maintainable scripts.

## File Conventions

- Use `#!/usr/bin/env bash` for bash scripts.
- Set strict mode: `set -euo pipefail` and `IFS=$'\n\t'`.
- All executable scripts should have executable bit set (`chmod +x`).

## Strict Mode Template

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

main() {
    # script logic
    echo "Running ${SCRIPT_NAME}"
}

main "$@"
```

## Best Practices

- Always quote variables: `"${variable}"`.
- Use `[[` over `[` for conditionals.
- Use `local` for function variables and `readonly` for constants.
- Redirect error output to stderr: `echo "error" >&2`.
- Run `shellcheck` for linting.
