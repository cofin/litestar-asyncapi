"""Hook to disallow `from __future__ import annotations` across the codebase."""

import ast
import sys
from pathlib import Path


def check_file(path: Path) -> bool:
    """Check if a Python file contains `from __future__ import annotations`.

    Parses the AST of the given file to inspect imports. If the file cannot
    be parsed due to a SyntaxError, falls back to a strict line-by-line match.

    Args:
        path: Path to the python file to inspect.

    Returns:
        True if the file contains the disallowed import, False otherwise.
    """
    if path.suffix != ".py":
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    try:
        tree = ast.parse(content, filename=str(path))
    except SyntaxError:
        return any(line.strip() == "from __future__ import annotations" for line in content.splitlines())

    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "__future__"
            and any(alias.name == "annotations" for alias in node.names)
        ):
            return True
    return False


def main(argv: list[str]) -> int:
    """Run future annotations check across provided command-line arguments.

    Args:
        argv: Command-line arguments containing file paths.

    Returns:
        0 if no files contain the disallowed import, 1 otherwise.
    """
    bad_files: list[str] = []
    for raw in argv[1:]:
        path = Path(raw)
        if check_file(path):
            bad_files.append(str(path))

    if not bad_files:
        return 0

    sys.stderr.write("Disallowed future import found. Remove `from __future__ import annotations` from:\n")
    for f in bad_files:
        sys.stderr.write(f" - {f}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
