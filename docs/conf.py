# Configuration file for the Sphinx documentation builder.
import datetime
import os
import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx

from litestar_asyncapi.__metadata__ import __version__

# -- Environmental Data ------------------------------------------------------
warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\..*")

__all__ = ("setup", "update_html_context")


# -- Project information -----------------------------------------------------
current_year = datetime.datetime.now(tz=datetime.timezone.utc).year
project = "Litestar AsyncAPI"
copyright = f"{current_year}, Litestar Organization"  # noqa: A001
release = os.getenv("_LITESTAR_ASYNCAPI_DOCS_BUILD_VERSION", __version__.rsplit(".")[0])
suppress_warnings = [
    "autosectionlabel.*",
    "ref.python",  # TODO: remove when https://github.com/sphinx-doc/sphinx/issues/4961 is fixed
    "ref",
    "autodoc.import_object",
    "autodoc",
    "myst.xref_missing",
    "misc.highlighting_failure",
    "app.add_directive",
    "app.add_extension",
    "docutils",
    "ref.doc",
    "toc.not_readable",
    "toc.not_included",
    "autosummary",
]

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinxcontrib.jquery",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "tools.sphinx_ext.missing_references",
    "tools.sphinx_ext.changelog",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "auto_pytabs.sphinx_ext",
    "sphinx_copybutton",
    "sphinx.ext.todo",
    "sphinx_click",
    "click_extra.sphinx",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinx_togglebutton",
    "sphinx_paramlinks",
    "sphinxcontrib.mermaid",
    "numpydoc",
    "sphinx_iconify",
    "sphinx_datatables",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "msgspec": ("https://jcristharif.com/msgspec/", None),
    "litestar": ("https://docs.litestar.dev/latest/", None),
    "anyio": ("https://anyio.readthedocs.io/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

PY_CLASS = "py:class"
PY_EXC = "py:exc"
PY_RE = r"py:.*"
PY_METH = "py:meth"
PY_ATTR = "py:attr"
PY_OBJ = "py:obj"
PY_FUNC = "py:func"
nitpicky = False
nitpick_ignore: list[str] = []
nitpick_ignore_regex: list[str] = []

auto_pytabs_min_version = (3, 10)
auto_pytabs_max_version = (3, 13)

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

numpydoc_show_class_members = False

autoclass_content = "class"
autodoc_class_signature = "separated"
autodoc_default_options = {"special-members": "__init__", "show-inheritance": True, "members": True}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
autodoc_warningiserror = False
autodoc_type_aliases = {
    "AsyncAPIConfig": "litestar_asyncapi.config.AsyncAPIConfig",
    "AsyncAPIPlugin": "litestar_asyncapi.plugin.AsyncAPIPlugin",
    "Union": "typing.Union",
    "Callable": "typing.Callable",
    "Any": "typing.Any",
    "Optional": "typing.Optional",
}

autosummary_generate = False
smartquotes = False

autosectionlabel_prefix_document = True

# Strip the dollar prompt when copying code
copybutton_prompt_text = "$ "

# -- Style configuration -----------------------------------------------------
html_theme = "shibuya"
html_title = "Litestar AsyncAPI"
html_short_title = "AsyncAPI"
pygments_style = "litestar-asyncapi-light"
pygments_dark_style = "litestar-asyncapi-dark"
todo_include_todos = True

html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
templates_path = ["_templates"]
html_js_files = ["versioning.js"]
html_css_files = ["style.css"]
html_show_sourcelink = True
html_copy_source = True

html_context = {
    "source_type": "github",
    "source_user": "litestar-org",
    "source_repo": "litestar-asyncapi",
    "current_version": "latest",
    "version": release,
}

# Mermaid configuration
mermaid_version = "11.2.0"
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis'
    }
});
"""

html_theme_options = {
    "logo_target": "/",
    "accent_color": "amber",
    "github_url": "https://github.com/litestar-org/litestar-asyncapi",
    "discord_url": "https://discord.gg/dSDXd4mKhp",
    "navigation_with_keys": True,
    "globaltoc_expand_depth": 2,
    "light_logo": "_static/logo-light.svg",
    "dark_logo": "_static/logo-dark.svg",
    "discussion_url": "https://discord.gg/dSDXd4mKhp",
    "nav_links": [
        {
            "title": "Docs",
            "children": [
                {
                    "title": "Getting Started",
                    "url": "getting-started",
                    "summary": "Installation and quickstart guide",
                },
                {
                    "title": "Usage",
                    "url": "usage/index",
                    "summary": "Detailed usage guides and tutorials",
                },
                {
                    "title": "API Reference",
                    "url": "reference/index",
                    "summary": "Comprehensive API documentation",
                },
            ],
        },
        {
            "title": "About",
            "children": [
                {
                    "title": "Changelog",
                    "url": "changelog",
                    "summary": "All changes for Litestar AsyncAPI",
                },
                {
                    "title": "Litestar Organization",
                    "summary": "Details about the Litestar organization, the team behind Litestar AsyncAPI",
                    "url": "https://litestar.dev/about/organization",
                    "icon": "org",
                },
                {
                    "title": "Releases",
                    "summary": "Explore the release process, versioning, and deprecation policy for Litestar AsyncAPI",
                    "url": "releases",
                    "icon": "releases",
                },
            ],
        },
        {
            "title": "Community",
            "children": [
                {
                    "title": "Contributing",
                    "summary": "Learn how to contribute to Litestar AsyncAPI",
                    "url": "contribution-guide",
                    "icon": "contributing",
                },
                {
                    "title": "Security",
                    "summary": "Litestar AsyncAPI security reporting process",
                    "url": "https://github.com/litestar-org/litestar-asyncapi/security/policy",
                    "icon": "security",
                },
                {
                    "title": "Code of Conduct",
                    "summary": "Litestar organization Code of Conduct",
                    "url": "https://github.com/litestar-org/.github/blob/main/CODE_OF_CONDUCT.md",
                    "icon": "coc",
                },
            ],
        },
    ],
}


def update_html_context(app: Any, pagename: Any, templatename: Any, context: Any, doctree: Any) -> None:  # type: ignore[misc]
    context["READTHEDOCS"] = False


def setup(app: "Sphinx") -> dict[str, Any]:
    app.connect("html-page-context", update_html_context)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
