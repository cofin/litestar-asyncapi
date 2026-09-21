"""Audit the documentation tree without modifying it."""

import argparse
import ast
import builtins
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = ROOT / "docs"
DEFAULT_README = ROOT / "README.md"
HEADING_MARKS = '=-~^"`:+*#'
CANONICAL_TERMS = (
    "AsyncAPIPlugin",
    "AsyncAPIConfig",
    "AsyncAPIGenerator",
    "SchemaRegistry",
    "WebSocket",
    "Playground",
    "ChannelsPlugin",
)
QUICKSTART_MARKER_THRESHOLD = 2


@dataclass(slots=True)
class PageReport:
    """Collected facts for one reStructuredText page."""

    path: Path
    words: int
    headings: list[tuple[int, str]]
    code_blocks: int
    literalincludes: list[str]
    generated_directives: int
    tutorial_signals: int
    toctree_entries: list[str]
    undefined_names: set[str] = field(default_factory=set)
    prompts: list[str] = field(default_factory=list)

    GUIDE_WORD_BUDGET: ClassVar[int] = 1200

    @property
    def relative_path(self) -> str:
        """Return the page path relative to the documentation root."""
        return self.path.as_posix()


def parse_page(path: Path, docs_root: Path) -> PageReport:
    """Collect deterministic metrics and review prompts for one page."""
    source = path.read_text(encoding="utf-8")
    headings = _headings(source)
    python_blocks = _python_code_blocks(source)
    includes = re.findall(r"^\.\. literalinclude::\s+(.+?)\s*$", source, flags=re.MULTILINE)
    generated = len(re.findall(r"^\.\. auto(?:module|class|function|method)::", source, flags=re.MULTILINE))
    tutorial_signals = len(re.findall(r"^\.\. (?:code-block|literalinclude)::", source, flags=re.MULTILINE))
    report = PageReport(
        path=path.relative_to(docs_root),
        words=len(re.findall(r"\b[\w'-]+\b", _without_directives(source))),
        headings=headings,
        code_blocks=len(re.findall(r"^\.\. code-block::", source, flags=re.MULTILINE)),
        literalincludes=includes,
        generated_directives=generated,
        tutorial_signals=tutorial_signals,
        toctree_entries=_toctree_entries(source),
    )
    report.undefined_names.update(_undefined_names(python_blocks[0]) if python_blocks else ())
    report.prompts.extend(_review_prompts(report))
    return report


def audit(docs_root: Path, readme: Path) -> int:
    """Print the documentation audit and return a process exit status."""
    pages = [parse_page(path, docs_root) for path in sorted(docs_root.rglob("*.rst"))]
    membership = _toctree_membership(pages)
    errors: list[str] = []

    print("Documentation source manifest")
    print("path | words | headings | code | includes | toctree")
    for page in pages:
        member = "yes" if _docname(page.path) in membership or page.path == Path("index.rst") else "no"
        print(
            f"{page.relative_path} | {page.words} | {len(page.headings)} | "
            f"{page.code_blocks} | {len(page.literalincludes)} | {member}"
        )
        if member == "no":
            errors.append(f"page is not in a toctree: {page.relative_path}")
        errors.extend(_literalinclude_errors(page, docs_root))

    print("\nReview prompts")
    prompts = [f"{page.relative_path}: {prompt}" for page in pages for prompt in page.prompts]
    for prompt in prompts or ["none"]:
        print(f"- {prompt}")

    corpus = "\n".join((docs_root / page.path).read_text(encoding="utf-8") for page in pages)
    print("\nVocabulary occurrences")
    for term in CANONICAL_TERMS:
        print(f"- {term}: {_occurrences(corpus, term)}")

    print("\nQuickstart duplication")
    quickstart_path = docs_root / "usage" / "quickstart.rst"
    if not quickstart_path.is_file():
        quickstart_path = docs_root / "getting-started.rst"
    print(f"- {_quickstart_duplication(readme, quickstart_path)}")

    print("\nStructural errors")
    for error in errors or ["none"]:
        print(f"- {error}")
    return 1 if errors else 0


def _headings(source: str) -> list[tuple[int, str]]:
    """Extract sections and heading levels from reStructuredText source."""
    lines = source.splitlines()
    headings: list[tuple[int, str]] = []
    marks: list[str] = []
    for index in range(len(lines) - 1):
        title = lines[index].strip()
        underline = lines[index + 1].strip()
        if not title or len(underline) < len(title) or len(set(underline)) != 1 or underline[0] not in HEADING_MARKS:
            continue
        mark = underline[0]
        if mark not in marks:
            marks.append(mark)
        headings.append((marks.index(mark) + 1, title))
    return headings


def _python_code_blocks(source: str) -> list[str]:
    """Extract python code block contents from reStructuredText source."""
    lines = source.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        match = re.match(r"^\.\. code-block::\s+python\s*$", lines[index])
        if match is None:
            index += 1
            continue
        index += 1
        while index < len(lines) and (not lines[index].strip() or lines[index].lstrip().startswith(":")):
            index += 1
        body: list[str] = []
        while index < len(lines) and (not lines[index].strip() or lines[index].startswith("   ")):
            body.append(lines[index][3:] if lines[index].startswith("   ") else "")
            index += 1
        blocks.append("\n".join(body).rstrip())
    return blocks


def _undefined_names(block: str) -> set[str]:
    """Parse python code block AST and detect undefined name references."""
    try:
        tree = ast.parse(block)
    except SyntaxError:
        return {"<code block does not parse>"}
    defined = set(dir(builtins))
    loaded: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
            defined.update(
                argument.arg for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
            )
        elif isinstance(node, ast.Import):
            defined.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            defined.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loaded.add(node.id)
    return loaded - defined


def _review_prompts(report: PageReport) -> list[str]:
    """Generate style, heading, and complexity review prompts for a page."""
    prompts: list[str] = []
    if report.words > report.GUIDE_WORD_BUDGET and report.path.parts[0] != "reference":
        prompts.append(f"review length ({report.words} words; guide threshold {report.GUIDE_WORD_BUDGET})")
    previous = 0
    for level, heading in report.headings:
        if previous and level > previous + 1:
            prompts.append(f"review heading hierarchy near {heading!r}")
        previous = level
        words = heading.split()
        if len(words) > 1 and sum(word[:1].isupper() for word in words[1:]) > len(words[1:]) / 2:
            prompts.append(f"review sentence case for heading {heading!r}")
    if report.generated_directives and report.tutorial_signals:
        prompts.append("page mixes generated API directives with tutorial code")
    if report.undefined_names:
        prompts.append(f"review primary Python block names: {', '.join(sorted(report.undefined_names))}")
    return prompts


def _toctree_entries(source: str) -> list[str]:
    """Collect document references from toctree directives in source."""
    lines = source.splitlines()
    entries: list[str] = []
    index = 0
    while index < len(lines):
        if not re.match(r"^\.\. toctree::\s*$", lines[index]):
            index += 1
            continue
        index += 1
        indent: int | None = None
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if not stripped:
                index += 1
                continue
            match = re.match(r"^(\s+)", line)
            if not match:
                break
            if indent is None:
                indent = len(match.group(1))
            if len(match.group(1)) < indent:
                break
            if not stripped.startswith(":"):
                entry = stripped
                if "<" in entry and entry.endswith(">"):
                    entry = entry.split("<", 1)[1].rstrip(">").strip()
                entries.append(entry)
            index += 1
    return entries


def _toctree_membership(pages: list[PageReport]) -> set[str]:
    """Build the complete set of reachable document names from all toctrees."""
    membership: set[str] = set()
    for page in pages:
        parent = page.path.parent
        for entry in page.toctree_entries:
            if entry.startswith(("http://", "https://")):
                continue
            if entry.startswith("/"):
                target = Path(entry.lstrip("/")).with_suffix("")
            else:
                target = (parent / entry).with_suffix("")
            membership.add(target.as_posix())
    return membership


def _literalinclude_errors(page: PageReport, docs_root: Path) -> list[str]:
    """Identify broken literalinclude targets on a given page."""
    source_dir = (docs_root / page.path).parent
    return [
        f"missing literalinclude from {page.relative_path}: {include}"
        for include in page.literalincludes
        if not (source_dir / include).resolve().is_file()
    ]


def _quickstart_duplication(readme: Path, quickstart: Path) -> str:
    """Detect whether quickstart snippets drift between README and documentation."""
    if not quickstart.is_file() or not readme.is_file():
        return "quickstart file not found for comparison"
    readme_source = readme.read_text(encoding="utf-8")
    docs_source = quickstart.read_text(encoding="utf-8")
    markers = ("AsyncAPIPlugin", "AsyncAPIConfig", "Litestar")
    shared = [marker for marker in markers if marker in readme_source and marker in docs_source]
    if len(shared) >= QUICKSTART_MARKER_THRESHOLD:
        return "README and docs share canonical quickstart markers; review them together when either changes"
    return "no likely competing quickstart detected"


def _without_directives(source: str) -> str:
    """Strip reStructuredText directive lines for word counting."""
    return re.sub(r"^\s*\.\..*$", "", source, flags=re.MULTILINE)


def _docname(path: Path) -> str:
    """Convert page file path to Sphinx document name."""
    return path.with_suffix("").as_posix()


def _occurrences(source: str, term: str) -> int:
    """Count case-insensitive term occurrences in corpus."""
    return len(re.findall(re.escape(term), source, flags=re.IGNORECASE))


def main() -> int:
    """Run the command-line audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS, help="Documentation source directory")
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="Project README path")
    args = parser.parse_args()
    return audit(args.docs.resolve(), args.readme.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
