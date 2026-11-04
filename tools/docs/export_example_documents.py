"""Export the AsyncAPI document of every runnable documentation example.

Each module under ``docs/examples/`` defines a module-level ``app``. The tool imports it, asks
its ``AsyncAPIPlugin`` for the canonical document and writes it to ``docs/_generated/<name>.json``,
where ``<name>`` is the example's directory for ``app.py`` packages and its file stem otherwise.
The output directory is recreated on every run so removed examples leave no stale documents,
and pages include these files instead of hand-written output.
"""

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

from litestar import Litestar

from litestar_asyncapi import AsyncAPIPlugin

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "docs" / "examples"
OUTPUT = ROOT / "docs" / "_generated"


def example_files() -> list[Path]:
    """Return every runnable example module, excluding package initializers."""
    return sorted(path for path in EXAMPLES.rglob("*.py") if path.name != "__init__.py")


def document_name(path: Path) -> str:
    """Return the output stem for an example module."""
    relative = path.relative_to(EXAMPLES)
    parts = relative.parent.parts if relative.name == "app.py" else relative.with_suffix("").parts
    return "-".join(parts)


def load_example(path: Path) -> ModuleType:
    """Import an example module under a unique name so its annotations resolve."""
    name = "docs_example_" + "_".join(path.relative_to(EXAMPLES).with_suffix("").parts)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        msg = f"{path}: cannot be imported"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def export(path: Path) -> Path:
    """Write the canonical document of one example and return the written file."""
    app = getattr(load_example(path), "app", None)
    if not isinstance(app, Litestar):
        msg = f"{path}: module-level 'app' must be a Litestar application"
        raise TypeError(msg)
    document = json.loads(app.plugins.get(AsyncAPIPlugin).get_asyncapi_json(app))
    target = OUTPUT / f"{document_name(path)}.json"
    target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    """Export every example document and return a process exit code."""
    files = example_files()
    if not files:
        print(f"No examples found under {EXAMPLES}", file=sys.stderr)
        return 1
    shutil.rmtree(OUTPUT, ignore_errors=True)
    OUTPUT.mkdir(parents=True)
    for path in files:
        print(f"Exported: {export(path).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
