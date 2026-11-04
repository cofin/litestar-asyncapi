---
type: Reference
title: "Distribution Lanes"
description: Distribution Lanes reference for the asyncapi-release-ci skill.
tags: [skills, asyncapi-release-ci, distribution-lanes]
---

# Distribution Lanes

How build, test and publish targets compose into the single tested artifact.

## Lane map

| Lane | Entry | Proves | Requires |
| --- | --- | --- | --- |
| Static | `make lint` | prek hooks, `mypy` strict, `pyright`, `slotscheck`, `zizmor`, doc markers, PEP 723 blocks | `make install` |
| Source tests | `make test` / `make coverage` | behavior in the checkout; coverage floor 80 | `make install` |
| Focused tests | `uv run pytest <path> -q --no-cov` | one module without the global coverage floor | `make install` |
| Packaged UI | `make js-install build js-test` | locked npm tree, Vite output, Vitest view logic, wheel+sdist asset completeness | Node (`.nvmrc`) |
| Official contract | `make validate-asyncapi` | `@asyncapi/specs` schemas + `@asyncapi/parser` accept exported 3.0/3.1 fixtures and reject isolated mutations | Node (`.nvmrc`) |
| Browser | `make browser-test` | Playwright Chromium against `tools/frontend/tests/server.py` | `npx playwright install chromium` |
| Installed Python | `make installed-test PYTHON_VERSION=X LITESTAR_BOUNDARY=minimum\|latest` | wheel imports from site-packages, minimal generation, full tests outside the checkout | built `dist/*.whl` |
| Installed browser | `make browser-test-installed PYTHON_VERSION=X` | installed manifest hash equals source manifest; browser suite against installed wheel | built wheel, Node (`.nvmrc`) |
| Docs | `make docs docs-linkcheck` | Sphinx HTML build and external links | docs group |

## `make build`

1. `js-build` runs `vite build` with `vite.config.ts`: `outDir: src/litestar_asyncapi/assets/ui`, `emptyOutDir: true`, `manifest: manifest.json`, bundled `THIRD-PARTY-LICENSES.md`, entries `tools/frontend/react.ts` and `tools/frontend/scalar.ts`.
2. `uv build` produces wheel and sdist; `pyproject.toml::tool.hatch.build.targets.{wheel,sdist}.artifacts` force-include `src/litestar_asyncapi/assets/**`.
3. `tools/frontend/tests/distribution.py::check_assets` asserts every file under `assets/`, every manifest `file`/`css` entry and the license file exist in both archives.

`emptyOutDir` deletes stale hashed bundles; commit additions and deletions together.

## `installed-test`

`Makefile::installed-test`:

1. Copies `src/tests` and `pyproject.toml` into a `mktemp -d` workdir with an `EXIT` trap.
2. Exports the locked `tests` group (`uv export --frozen --only-group tests`).
3. Installs the wheel plus the boundary framework pin (`litestar==2.24.0` or `litestar>=2.24,<3`).
4. Asserts the import resolves under `sys.prefix` and `get_asyncapi_schema(...)["asyncapi"] == "3.1.0"` before any test dependency is installed.
5. Installs test requirements and `litestar[standard,attrs,pydantic]` at the boundary; asserts `minimum` resolved exactly `2.24.0`.
6. Runs `python -m pytest tests --no-cov -q` from the workdir.

When raising the minimum Litestar version, update `project.dependencies`, both pins in `installed-test`, and the `minimum` assertion together.

## CI composition

- `ci.yml::distribution` calls `distribution.yml`; `ci.yml::test_python` fans out `test.yml` over Python 3.10–3.14 x `minimum`/`latest` and downloads `tested-distribution`.
- Coverage runs only where `coverage` input is true (3.12/minimum) and uploads `coverage-xml` for `ci.yml::codecov`.
- `publish.yml` (on `release: published` or `workflow_dispatch`) calls `distribution.yml`, then `pypi` downloads `tested-distribution` into `dist` and publishes via trusted publishing.

## Release targets

`make release bump=major|minor|patch` runs `docs`, `clean`, `build`, then `bump-my-version bump` and `uv lock --upgrade-package litestar-asyncapi`. `make pre-release version=X.Y.Z-alpha.N` does the same with an explicit version. `tool.bumpversion` sets `commit = false` and `tag = false`; the release itself is created on GitHub by the maintainer. These targets run only when the user asks.
