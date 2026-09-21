"""Verify distribution assets and all manifest references after a release build."""

import json
import tarfile
from pathlib import Path
from zipfile import ZipFile

__all__ = ("check_assets",)


def check_assets(names: set[str], prefix: str) -> None:
    asset_root = Path("src/litestar_asyncapi/assets")
    expected = {prefix + path.relative_to(asset_root).as_posix() for path in asset_root.rglob("*") if path.is_file()}
    missing = expected - names
    if missing:
        message = f"Distribution is missing packaged assets: {sorted(missing)}"
        raise AssertionError(message)
    manifest = json.loads((asset_root / "ui/manifest.json").read_text())
    for entry in manifest.values():
        for filename in [entry["file"], *entry.get("css", [])]:
            assert prefix + "ui/" + filename in names
    assert prefix + "ui/THIRD-PARTY-LICENSES.md" in names


if __name__ == "__main__":
    wheel = max(Path("dist").glob("*.whl"), key=lambda path: path.stat().st_mtime)
    sdist = max(Path("dist").glob("*.tar.gz"), key=lambda path: path.stat().st_mtime)
    with ZipFile(wheel) as archive:
        check_assets(set(archive.namelist()), "litestar_asyncapi/assets/")
    with tarfile.open(sdist) as archive:
        names = set(archive.getnames())
        root = next(iter(names)).split("/")[0]
        check_assets(names, root + "/src/litestar_asyncapi/assets/")
    print("Wheel and sdist contain every asset, manifest entry and bundled license.")
