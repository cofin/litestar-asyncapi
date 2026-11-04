"""Write redirect stubs from every former URL to its page on the Zensical site.

The Sphinx site served flat ``<page>.html`` files. The Zensical site uses directory URLs, so each
former file becomes a small HTML stub that forwards to the new page and keeps the URL fragment,
which preserves deep links such as ``usage/websocket-handlers.html#server-sent-events``. Reference
pages that were renamed keep their former directory URLs the same way, through an ``index.html`` stub.

Built pages are also compacted: the indentation the theme templates leave at the start of each line is
removed everywhere except inside ``pre``, ``textarea``, ``script`` and ``style`` elements, where
whitespace is significant. This keeps API reference pages within their size budget.
"""

import html
import importlib
import json
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"

REDIRECTS: dict[str, str] = {
    "getting-started.html": "learn/installation/",
    "usage/index.html": "learn/",
    "usage/quickstart.html": "learn/installation/",
    "usage/concepts.html": "learn/concepts/",
    "usage/websocket-handlers.html": "learn/websocket-handlers/",
    "usage/decorators.html": "learn/decorators/",
    "usage/schema-generation.html": "learn/schema-generation/",
    "usage/channels-plugin.html": "integrations/channels-plugin/",
    "usage/renderers.html": "integrations/documentation-ui/",
    "usage/security-and-servers.html": "integrations/security-and-servers/",
    "examples/index.html": "learn/examples/",
    "examples/README.html": "learn/examples/",
    "migration.html": "project/migration/",
    "changelog.html": "project/changelog/",
    "contribution-guide.html": "project/contribution-guide/",
    "reference/api.html": "reference/",
    "reference/core.html": "reference/plugin/",
    "reference/plugins.html": "reference/renderers/",
    "reference/spec.html": "reference/spec/",
    "reference/extractors.html": "reference/generator/",
    "reference/schema-generation.html": "reference/schema/",
    "genindex.html": "reference/",
    "py-modindex.html": "reference/",
    "search.html": "./",
    "reference/core/index.html": "reference/plugin/",
    "reference/plugins/index.html": "reference/renderers/",
    "reference/extractors/index.html": "reference/generator/",
    "reference/schema-generation/index.html": "reference/schema/",
}
"""Former page path mapped to the URL that replaced it, both relative to the site root."""

PRESERVED = re.compile(r"<(pre|textarea|script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
INDENTATION = re.compile(r"\n\s+")

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{href}">
<script>const fragments = {fragments}; let fragment = location.hash.slice(1); while (fragment && !Object.hasOwn(fragments, fragment)) fragment = fragment.includes('.') ? fragment.slice(0, fragment.lastIndexOf('.')) : ''; location.replace(fragments[fragment] || {target} + location.hash);</script>
<meta http-equiv="refresh" content="0; url={href}">
</head>
<body>
<p>This page has moved to <a href="{href}">{href}</a>.</p>
</body>
</html>
"""


def relative_target(source: str, target: str) -> str:
    """Return the target URL relative to the directory that serves the stub."""
    relative = posixpath.relpath(target, posixpath.dirname(source) or ".")
    return "./" if relative == "." else f"{relative}/"


def legacy_api_fragments(site: Path) -> dict[str, tuple[str, str]]:
    """Map former implementation-module API anchors to the public anchors actually rendered."""
    modules = [
        importlib.import_module(name)
        for name in (
            "litestar_asyncapi.asyncapi.schema_generation",
            "litestar_asyncapi.asyncapi.extractors",
            "litestar_asyncapi.spec",
            "litestar_asyncapi",
        )
    ]
    fragments = {}
    for page in sorted(site.rglob("index.html")):
        target = page.parent.relative_to(site).as_posix() + "/"
        for encoded in re.findall(r'\bid="([^"]+)"', page.read_text(encoding="utf-8")):
            anchor = html.unescape(encoded)
            if anchor.startswith("litestar_asyncapi."):
                fragments[anchor] = (target, anchor)
            for module in modules:
                if not anchor.startswith(module.__name__ + "."):
                    continue
                name, _, member = anchor.removeprefix(module.__name__ + ".").partition(".")
                value = getattr(module, name, None)
                origin = getattr(value, "__module__", None)
                if origin:
                    suffix = f".{member}" if member else ""
                    fragments[f"{origin}.{name}{suffix}"] = (target, anchor)
                    if name in {"AsyncAPIPlugin", "AsyncAPIUIRenderPlugin"}:
                        fragments[f"litestar_asyncapi.plugins.{name}{suffix}"] = (target, anchor)
                break
    return fragments


def write_redirects(site: Path) -> list[Path]:
    """Write one stub per former URL and return the written files."""
    written = []
    fragments = legacy_api_fragments(site)
    for source, target in REDIRECTS.items():
        path = site / source
        if path.exists():
            msg = f"{source}: a built page already exists where the redirect stub belongs"
            raise FileExistsError(msg)
        href = relative_target(source, target)
        path.parent.mkdir(parents=True, exist_ok=True)
        targets = {
            old: relative_target(source, destination) + "#" + anchor
            for old, (destination, anchor) in fragments.items()
            if source.startswith("reference/")
        }
        path.write_text(
            STUB.format(
                href=html.escape(href, quote=True),
                target=json.dumps(href),
                fragments=json.dumps(targets).replace("<", "\\u003c"),
            ),
            encoding="utf-8",
        )
        written.append(path)
    return written


def compact(text: str) -> str:
    """Remove line indentation and blank lines outside whitespace-sensitive elements."""
    parts = []
    position = 0
    for match in PRESERVED.finditer(text):
        parts.append(INDENTATION.sub("\n", text[position : match.start()]))
        parts.append(match.group(0))
        position = match.end()
    parts.append(INDENTATION.sub("\n", text[position:]))
    return "".join(parts)


def compact_pages(site: Path) -> int:
    """Compact every built page in place and return the number of bytes saved."""
    saved = 0
    for page in site.rglob("*.html"):
        original = page.read_text(encoding="utf-8")
        compacted = compact(original)
        saved += len(original.encode()) - len(compacted.encode())
        page.write_text(compacted, encoding="utf-8")
    return saved


def main() -> int:
    """Compact the built pages, write the redirect stubs and return a process exit code."""
    if not (SITE / "index.html").is_file():
        print(f"{SITE} has no built site; run the Zensical build first", file=sys.stderr)
        return 1
    saved = compact_pages(SITE)
    written = write_redirects(SITE)
    print(f"Compacted pages by {saved} bytes and wrote {len(written)} redirect stubs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
