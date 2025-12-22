import os
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

current_path = Path(__file__).parent.parent.resolve()
sys.path.append(str(current_path))

project = "litestar-asyncapi"
version = metadata.version("litestar-asyncapi")
copyright = "2025, Litestar-Org"  # noqa: A001
author = "Litestar-Org"
release = os.getenv("_LITESTAR_ASYNCAPI_DOCS_BUILD_VERSION", version.rsplit(".")[0])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "litestar": ("https://docs.litestar.dev/latest/", None),
}

napoleon_google_docstring = True
autoclass_content = "class"
autodoc_default_options = {"special-members": "__init__", "show-inheritance": True, "members": True}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
autosectionlabel_prefix_document = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "litestar_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["style.css"]
html_title = "Litestar AsyncAPI"
html_favicon = "_static/favicon.ico"
html_context = {
    "source_type": "github",
    "source_user": "litestar-org",
    "source_repo": "litestar-asyncapi",
}

brand_colors = {
    "--brand-primary": {"rgb": "46, 132, 255", "hex": "#2e84ff"},
    "--brand-secondary": {"rgb": "32, 32, 32", "hex": "#202020"},
    "--brand-tertiary": {"rgb": "161, 173, 161", "hex": "#A1ADA1"},
    "--brand-green": {"rgb": "0, 245, 151", "hex": "#00f597"},
    "--brand-alert": {"rgb": "243, 96, 96", "hex": "#f36060"},
    "--brand-dark": {"rgb": "0, 0, 0", "hex": "#000000"},
    "--brand-light": {"rgb": "235, 221, 221", "hex": "#ebdddd"},
}

html_theme_options: dict[str, Any] = {
    "logo_target": "/",
    "github_url": "https://github.com/litestar-org/litestar-asyncapi",
    "github_repo_name": "Litestar AsyncAPI",
    "nav_links": [
        {"title": "Home", "url": "https://litestar-org.github.io/litestar-asyncapi/"},
        {"title": "Docs", "url": "https://litestar-org.github.io/litestar-asyncapi/latest/"},
        {"title": "Code", "url": "https://github.com/litestar-org/litestar-asyncapi"},
    ],
    "use_page_nav": True,
    "light_logo": "_static/logo-light.svg",
    "dark_logo": "_static/logo-dark.svg",
    "brand_colors": brand_colors,
}
