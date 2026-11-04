"""Check the docstrings that the API reference renders.

The reference reads source statically, so a dataclass field without a docstring directly below it
renders with an empty description. The scan fails when:

1. A field of a public ``@dataclass`` in a public module has no inline docstring.
2. A public module, class, function or field docstring contains an internal planning label, such as
   a task id, chapter or phase number, or a ``TODO`` marker.

Modules and names that start with an underscore are private and skipped, except ``__init__.py``.
"""

import argparse
import ast
import re
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "src" / "litestar_asyncapi"
PLANNING_LABEL = re.compile(
    r"\b(?:chapter|phase|milestone|sprint|wave)\s+\d+\b|\bt\d{2}\b|\b(?:TODO|FIXME|XXX)\b|\bflow[_ ]id\b", re.IGNORECASE
)


def is_public_module(path: Path, root: Path) -> bool:
    """Return whether no part of the module path below ``root`` is private."""
    parts = path.relative_to(root).with_suffix("").parts
    return not any(part.startswith("_") and part != "__init__" for part in parts)


def is_dataclass(node: ast.ClassDef) -> bool:
    """Return whether a class is decorated with ``dataclass`` in any spelling."""
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", None)
        if name == "dataclass":
            return True
    return False


def string_value(node: ast.stmt | None) -> str | None:
    """Return the text of a bare string statement, or ``None`` for anything else."""
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
        return node.value.value
    return None


def is_class_var(annotation: ast.expr) -> bool:
    """Return whether an annotation declares a ``ClassVar``, which is not a dataclass field."""
    target = annotation.value if isinstance(annotation, ast.Subscript) else annotation
    name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", None)
    return name == "ClassVar"


def public_docstrings(tree: ast.Module) -> Iterator[tuple[int, str, str]]:
    """Yield the line, owner and text of every docstring a reader of the reference can see."""
    module_doc = string_value(tree.body[0] if tree.body else None)
    if module_doc is not None:
        yield 1, "module", module_doc
    stack: list[tuple[str, list[ast.stmt]]] = [("", tree.body)]
    while stack:
        prefix, body = stack.pop()
        for index, node in enumerate(body):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                qualname = f"{prefix}{node.name}"
                doc = ast.get_docstring(node, clean=False)
                if doc is not None:
                    yield node.lineno, qualname, doc
                if isinstance(node, ast.ClassDef):
                    stack.append((f"{qualname}.", node.body))
            elif isinstance(node, (ast.AnnAssign, ast.Assign)):
                targets = [node.target] if isinstance(node, ast.AnnAssign) else node.targets
                names = [target.id for target in targets if isinstance(target, ast.Name)]
                doc = string_value(body[index + 1] if index + 1 < len(body) else None)
                if doc is not None and names and not names[0].startswith("_"):
                    yield node.lineno, f"{prefix}{names[0]}", doc


def missing_field_docstrings(tree: ast.Module) -> Iterator[tuple[int, str]]:
    """Yield the line and qualified name of every undocumented public dataclass field."""
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name.startswith("_") or not is_dataclass(node):
            continue
        for index, statement in enumerate(node.body):
            if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
                continue
            name = statement.target.id
            if name.startswith("_") or is_class_var(statement.annotation):
                continue
            following = node.body[index + 1] if index + 1 < len(node.body) else None
            if string_value(following) is None:
                yield statement.lineno, f"{node.name}.{name}"


def scan(root: Path) -> list[str]:
    """Return one error line per problem found in the public modules below ``root``."""
    errors = []
    for path in sorted(root.rglob("*.py")):
        if not is_public_module(path, root):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        errors.extend(
            f"{label}:{line}: {name} has no inline docstring" for line, name in missing_field_docstrings(tree)
        )
        for line, owner, text in public_docstrings(tree):
            match = PLANNING_LABEL.search(text)
            if match:
                errors.append(f"{label}:{line}: {owner} docstring contains the planning label {match.group(0)!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Scan the package, or the given directories, and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("roots", nargs="*", type=Path, default=[PACKAGE], help="package directories to scan")
    arguments = parser.parse_args(argv)
    errors = [error for root in arguments.roots for error in scan(root.resolve())]
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"{len(errors)} public docstring errors", file=sys.stderr)
        return 1
    print("Every public dataclass field has an inline docstring and no docstring has a planning label")
    return 0


if __name__ == "__main__":
    sys.exit(main())
