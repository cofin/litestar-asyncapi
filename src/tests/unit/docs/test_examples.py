import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
from litestar import Litestar
from litestar.testing import TestClient

EXAMPLES = Path(__file__).resolve().parents[4] / "docs" / "examples"

if not EXAMPLES.is_dir():
    pytest.skip("documentation examples are only available in a source checkout", allow_module_level=True)

EXAMPLE_FILES = sorted(path for path in EXAMPLES.rglob("*.py") if path.name != "__init__.py")
REQUEST_HEADERS = {"mounted_docs.py": {"authorization": "demo-token"}}


def load_example(path: Path) -> ModuleType:
    relative = path.relative_to(EXAMPLES).with_suffix("")
    name = "docs_example_" + "_".join(relative.parts)
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_examples_are_discovered() -> None:
    assert EXAMPLE_FILES


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=lambda path: path.relative_to(EXAMPLES).as_posix())
def test_example_serves_asyncapi_document(path: Path) -> None:
    app = load_example(path).app
    assert isinstance(app, Litestar)

    with TestClient(app=app) as client:
        response = client.get(app.route_reverse("asyncapi:json"), headers=REQUEST_HEADERS.get(path.name, {}))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.asyncapi+json")
    assert response.json()["asyncapi"] == "3.1.0"
