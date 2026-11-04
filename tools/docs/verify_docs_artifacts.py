"""Verify the built documentation site before it is published.

The check fails when:

1. ``site/objects.inv`` is missing, empty or not a Sphinx version 2 inventory.
2. A former Sphinx URL has no redirect stub, or a stub points at a page that does not exist.
3. An internal ``href`` or ``src`` in ``site/**/*.html`` names a missing file, or its fragment
   names no ``id`` or ``name`` on the target page.

External URLs are left to the separate ``lychee`` link check.
"""

import sys
from functools import cache
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from tools.docs.postbuild import REDIRECTS, relative_target

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SITE_PREFIX = "/litestar-asyncapi/"
LINK_ATTRIBUTES = {"a": "href", "link": "href", "img": "src", "script": "src", "source": "src"}


class PageParser(HTMLParser):
    """Collect anchor targets and outgoing internal references from one HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("id", "name"):
            if values.get(key) and (key == "id" or tag == "a"):
                self.anchors.add(str(values[key]))
        attribute = LINK_ATTRIBUTES.get(tag)
        if attribute and values.get(attribute):
            self.references.append(str(values[attribute]))


@cache
def parse(path: Path) -> PageParser:
    """Parse a built page once."""
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def resolve(page: Path, reference: str) -> tuple[Path, str] | None:
    """Return the file and fragment an internal reference points at, or ``None`` for external URLs."""
    parts = urlsplit(reference)
    if parts.scheme or parts.netloc or reference.startswith("//"):
        return None
    path = unquote(parts.path)
    if not path:
        return page, unquote(parts.fragment)
    if path.startswith(SITE_PREFIX):
        target = SITE / path.removeprefix(SITE_PREFIX)
    elif path.startswith("/"):
        target = SITE / path.lstrip("/")
    else:
        target = page.parent / PurePosixPath(path)
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target.resolve(), unquote(parts.fragment)


def check_inventory(site: Path) -> list[str]:
    """Check that the Sphinx inventory exists and has a version 2 header."""
    inventory = site / "objects.inv"
    if not inventory.is_file() or inventory.stat().st_size == 0:
        return [f"{inventory}: missing or empty"]
    if not inventory.read_bytes().startswith(b"# Sphinx inventory version 2"):
        return [f"{inventory}: not a Sphinx version 2 inventory"]
    return []


def check_redirects(site: Path) -> list[str]:
    """Check that every former URL has a stub that resolves to its locked page."""
    errors = []
    for source, target in REDIRECTS.items():
        stub = site / source
        if not stub.is_file():
            errors.append(f"{source}: redirect stub is missing")
            continue
        href = relative_target(source, target)
        if href not in parse(stub).references:
            errors.append(f"{source}: redirect stub does not link to {href}")
        destination = site / target / "index.html"
        if not destination.is_file():
            errors.append(f"{source}: redirect target {target} does not exist")
    return errors


def check_links(site: Path) -> list[str]:
    """Check every internal reference and fragment in the built pages."""
    errors = []
    for page in sorted(site.rglob("*.html")):
        for reference in parse(page).references:
            resolved = resolve(page, reference)
            if resolved is None:
                continue
            target, fragment = resolved
            label = f"{page.relative_to(site)}: {reference}"
            if not target.is_file():
                errors.append(f"{label}: target does not exist")
            elif fragment and target.suffix == ".html" and fragment not in parse(target).anchors:
                errors.append(f"{label}: anchor #{fragment} does not exist")
    return errors


def main() -> int:
    """Run every artifact check and return a process exit code."""
    if not (SITE / "index.html").is_file():
        print(f"{SITE} has no built site; run make docs", file=sys.stderr)
        return 1
    errors = check_inventory(SITE) + check_redirects(SITE) + check_links(SITE)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"{len(errors)} documentation artifact errors", file=sys.stderr)
        return 1
    pages = sum(1 for _ in SITE.rglob("*.html"))
    print(f"Verified objects.inv, {len(REDIRECTS)} redirects and internal links across {pages} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
