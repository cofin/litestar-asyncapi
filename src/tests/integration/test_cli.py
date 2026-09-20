import json
import subprocess
import sys
from pathlib import Path

from litestar.testing import TestClient

from tests.fixtures.apps.cli import http_app

FIXTURE = Path(__file__).parents[1] / "fixtures" / "apps" / "cli.py"


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "litestar",
            "--app",
            "tests.fixtures.apps.cli:app",
            "--app-dir",
            str(FIXTURE.parents[3]),
            "asyncapi",
            "export",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_headless_export_matches_http() -> None:
    result = invoke()
    assert result.returncode == 0, result.stderr
    with TestClient(http_app) as client:
        assert json.loads(result.stdout) == client.get("/asyncapi/asyncapi.json").json()
    document = json.loads(result.stdout)
    assert document["servers"]["local"] == {"host": "localhost:8000", "protocol": "ws"}
    messages = document["channels"]["/events"]["messages"]
    assert messages["ListenerHandler_receive"]["examples"] == [{"payload": ["amount:2.50", 1]}]
    assert invoke().stdout == result.stdout


def test_output_protection_and_yaml(tmp_path: Path) -> None:
    import yaml

    output = tmp_path / "schema.yaml"
    result = invoke("--format", "yaml", "--output", str(output))
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    expected = json.loads(invoke().stdout)
    assert yaml.safe_load(output.read_text()) == expected
    original = output.read_bytes()
    assert invoke("--format", "yaml").stdout.encode() == original
    output.write_text("keep me")
    refused = invoke("--output", str(output))
    assert refused.returncode != 0
    assert refused.stdout == ""
    assert "--overwrite" in refused.stderr
    assert output.read_text() == "keep me"
    assert invoke("--output", str(output), "--overwrite").returncode == 0
    assert json.loads(output.read_text()) == expected


def test_write_failure_and_invalid_format(tmp_path: Path) -> None:
    failed = invoke("--output", str(tmp_path / "missing" / "schema.json"))
    assert failed.returncode != 0
    assert failed.stdout == ""
    assert "AsyncAPI export failed" in failed.stderr
    invalid = invoke("--format", "xml")
    assert invalid.returncode != 0
    assert invalid.stdout == ""
    assert "Invalid value" in invalid.stderr
