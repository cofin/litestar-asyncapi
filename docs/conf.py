"""Sphinx configuration for Litestar AsyncAPI documentation."""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx

from litestar_asyncapi.__metadata__ import __version__

sys.path.append(str(Path(__file__).parent.parent.resolve()))

__all__ = ("setup",)

project = "Litestar AsyncAPI"
copyright = "2026, Litestar Organization"
author = "Litestar Organization"
version = __version__
release = os.getenv("_LITESTAR_ASYNCAPI_DOCS_BUILD_VERSION", version.rsplit(".")[0])

asyncapi_light_style = "tools.sphinx_ext.pygments_styles.LitestarAsyncApiLightStyle"
asyncapi_dark_style = "tools.sphinx_ext.pygments_styles.LitestarAsyncApiDarkStyle"
pygments_style = asyncapi_light_style
pygments_dark_style = asyncapi_dark_style

try:
    from shibuya._pygments import ShibuyaPygmentsBridge
except ModuleNotFoundError:
    pass
else:
    ShibuyaPygmentsBridge.dark_style_name = asyncapi_dark_style

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "auto_pytabs.sphinx_ext",
    "sphinxcontrib.mermaid",
    "sphinx_paramlinks",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "litestar": ("https://docs.litestar.dev/latest/", None),
}

auto_pytabs_min_version = (3, 10)
auto_pytabs_max_version = (3, 13)

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

autoclass_content = "class"
autodoc_default_options = {"special-members": "__init__", "show-inheritance": True, "members": True}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

suppress_warnings = ["app.add_node", "ref.python", "autodoc", "duplicate", "autosectionlabel.*"]

copybutton_prompt_text = "$ "

html_theme = "shibuya"
html_title = "Litestar AsyncAPI"
html_short_title = "AsyncAPI"
html_favicon = "_static/favicon.ico"
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["style.css"]

html_context = {
    "source_type": "github",
    "source_user": "cofin",
    "source_repo": "litestar-asyncapi",
    "current_version": "latest",
    "version": release,
}

mermaid_version = "11.12.1"
mermaid_light_theme = "base"
mermaid_dark_theme = "base"
mermaid_height = "auto"
mermaid_init_config = {
    "startOnLoad": False,
    "flowchart": {"useMaxWidth": True, "htmlLabels": True, "curve": "basis", "padding": 12},
    "themeVariables": {
        "primaryColor": "#edb641",
        "primaryTextColor": "#202235",
        "primaryBorderColor": "#d4a438",
        "lineColor": "#94a3b8",
        "edgeLabelBackground": "transparent",
        "fontFamily": '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif',
        "fontSize": "15px",
    },
}

html_theme_options: dict[str, Any] = {
    "logo_target": "/",
    "accent_color": "amber",
    "github_url": "https://github.com/cofin/litestar-asyncapi",
    "discord_url": "https://discord.gg/litestar-919193495116337154",
    "discussion_url": "https://github.com/cofin/litestar-asyncapi/discussions",
    "navigation_with_keys": True,
    "globaltoc_expand_depth": 1,
    "light_logo": "_static/logo-light.svg",
    "dark_logo": "_static/logo-dark.svg",
    "nav_links": [
        {
            "title": "Docs",
            "children": [
                {"title": "Getting Started", "url": "getting-started", "summary": "Installation and quickstart guide"},
                {"title": "Usage", "url": "usage/index", "summary": "Detailed usage guides and tutorials"},
                {"title": "API Reference", "url": "reference/index", "summary": "Comprehensive API documentation"},
            ],
        },
        {
            "title": "About",
            "children": [
                {"title": "Changelog", "url": "changelog", "summary": "All changes for Litestar AsyncAPI"},
                {
                    "title": "Contributing",
                    "url": "contribution-guide",
                    "summary": "Learn how to contribute to Litestar AsyncAPI",
                },
            ],
        },
    ],
}


def setup(app: "Sphinx") -> dict[str, bool]:
    """Initialize Sphinx extensions including Shibuya theme integration."""
    app.setup_extension("shibuya")
    return {"parallel_read_safe": True, "parallel_write_safe": True}
