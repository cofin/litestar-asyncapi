---
name: asyncapi-release-ci
description: Use when editing Makefile targets (build, release, pre-release, installed-test, browser-test-installed, js-*, validate-*, zizmor, docs), pyproject.toml build/dependency/pytest/coverage/slotscheck/ruff/bumpversion config, package.json or package-lock.json, vite.config.ts, playwright.config.ts, .github/workflows/*.yml, .pre-commit-config.yaml, tools/ci/*.py, tools/validate_asyncapi.mjs, tools/docs_audit.py, tools/hooks/*.py, or PEP 723 blocks and doc markers in docs/examples.
---

# AsyncAPI Release & CI

<!-- truth: start -->
- One tested artifact: `.github/workflows/distribution.yml` (`workflow_call`) builds, validates and uploads `tested-distribution`; `test.yml` and `publish.yml` download it. Publishing never rebuilds.
- `make build` = `js-build` (Vite into `src/litestar_asyncapi/assets/ui/`) + `uv build` + `tools/frontend/tests/distribution.py::check_assets` on wheel and sdist.
- Built UI assets are committed and shipped through hatch `artifacts`; consumers need neither Node nor a CDN. Node (`.nvmrc`) is build/test-only (`package.json::engines`).
- Runtime dependency is `litestar>=2.24.0` with no upper cap; `installed-test` proves `minimum` (`litestar==2.24.0`) and `latest` (`litestar>=2.24,<3`) boundaries.
- `installed-test` installs the wheel into a temp venv outside the checkout, asserts `litestar_asyncapi.__file__` is under `sys.prefix`, generates a 3.1.0 document, then runs `pytest tests --no-cov -q`.
- CI matrix: Python 3.10–3.14 x `minimum`/`latest`; coverage XML only on 3.12/minimum.
- Every external Action pins a full 40-char SHA with a `# vX` comment; workflows default to `permissions: contents: read`; elevate per job only (`id-token: write` for PyPI/Pages).
- Every `actions/checkout` sets `persist-credentials: false`. Local reusable workflows use `uses: $/.github/workflows/<file>.yml`.
- `make zizmor` reports zero high/medium findings.
- Focused tests: `uv run pytest <path> -q --no-cov`. Global `--cov-fail-under=80` in `pyproject.toml::tool.pytest.ini_options.addopts` fails any partial run.
- `make lint` = prek, mypy, pyright, slotscheck, zizmor, validate-examples, validate-pep723. `make check-all` = lint + test + coverage.
- `make release` / `make pre-release` bump versions in `pyproject.toml` and `uv.lock` via bump-my-version (`commit = false`, `tag = false`). Run them only on explicit user request; never create, move or delete Git tags and never push.
- Package Python code never uses `from __future__ import annotations` (`tools/hooks/no_future_annotations.py`) and carries zero inline comments.
- Runnable `docs/examples/**/*.py` declare a PEP 723 block with `requires-python >=3.10` and a `litestar-asyncapi` dependency; `# start-example`/`# end-example` blocks compile standalone.
<!-- truth: end -->

## Scope

- `Makefile`: `install`, `build`, `js-*`, `release`, `pre-release`, `docs*`, `validate-*`, `export-asyncapi-fixture`, `test`, `coverage`, `type-check`, `prek`, `zizmor`, `slotscheck`, `lint`, `check-all`, `installed-test`, `browser-test-installed`.
- `pyproject.toml`: `project.dependencies`, `tool.hatch.build.*`, `dependency-groups`, `tool.pytest.ini_options`, `tool.coverage.*`, `tool.bumpversion`, `tool.ruff*`, `tool.mypy`, `tool.pyright`, `tool.slotscheck`, `tool.codespell`.
- `package.json`, `package-lock.json`, `vite.config.ts`, `playwright.config.ts`.
- `.github/workflows/{ci,test,distribution,publish,docs,pr-title}.yml`, `.pre-commit-config.yaml`.
- `tools/ci/validate_doc_markers.py`, `tools/ci/validate_pep723_blocks.py`, `tools/validate_asyncapi.mjs`, `tools/docs_audit.py`, `tools/hooks/no_future_annotations.py`, `tools/frontend/tests/distribution.py`.
- `docs/conf.py`, `docs/examples/**`.

## Seams

| Module | Interface | Implementation | Seam / Adapter |
| --- | --- | --- | --- |
| Tested distribution | `distribution.yml` artifact `tested-distribution` | `make build js-test validate-asyncapi browser-test installed-test browser-test-installed` | `actions/upload-artifact` / `download-artifact` handoff to `test.yml`, `publish.yml` |
| Installed compatibility | `make installed-test PYTHON_VERSION= LITESTAR_BOUNDARY=` | temp venv, `uv export --only-group tests`, boundary pins | `WHEEL ?= $(wildcard dist/*.whl)` |
| Packaged UI | `src/litestar_asyncapi/assets/ui/manifest.json` | `vite.config.ts` entries `react`, `scalar` | hatch `artifacts`; `distribution.py::check_assets` |
| Official contract gate | `make validate-asyncapi` | `tools/validate_asyncapi.mjs::validate`, `::verifyGate` | `export-asyncapi-fixture` via `litestar ... asyncapi export` on `tests.fixtures.apps.cli:app` |
| Static gates | `make lint` | prek hooks, mypy strict, pyright standard, slotscheck exclusions | `.pre-commit-config.yaml`, `pyproject.toml` tool tables |
| Doc examples | `make validate-examples`, `make validate-pep723` | `validate_doc_markers.py::validate_file`, `validate_pep723_blocks.py::validate_file` | `docs/examples/**/*.py` |

Dependency categories:

- **In-process**: ruff, mypy, pyright, slotscheck, pytest, the validators in `tools/ci/`.
- **Local-substitutable**: temp venvs and fixture exports (`installed-test`, `export-asyncapi-fixture`), Playwright `webServer` via `ASYNCAPI_BROWSER_SERVER`.
- **Remote-owned**: PyPI index, npm registry, upstream Actions pinned by SHA, prek hook repos pinned by `rev`.
- **External boundary**: PyPI trusted publishing (`environment: pypi`), GitHub Pages, Codecov upload.

## Workflow

1. Identify which lane the change touches: static gates, Python tests, packaged UI, installed distribution, docs, or publishing. Read [distribution-lanes.md](references/distribution-lanes.md) for lane composition.
2. Add behavior through an existing `Makefile` target and call that target from CI; keep workflow steps thin (`run: make <target>`).
3. For a new or replacement gate, prove it rejects an isolated violation (temporary file or mutation) before relying on it, then remove the probe.
4. For workflow edits, apply [workflow-hardening.md](references/workflow-hardening.md): SHA pin, version comment, least-privilege job permissions, `persist-credentials: false`, artifact handoff.
5. For dependency edits, keep `litestar>=2.24.0` uncapped in `project.dependencies`; adjust `installed-test` boundaries and lockfiles (`uv lock`, `npm ci`-compatible `package-lock.json`) together.
6. For frontend version bumps, rebuild with `make js-install build`, commit the regenerated `src/litestar_asyncapi/assets/ui/` tree, and rerun browser lanes.
7. Run the verification set for the touched lane; record any skipped lane and why.

## Verification

```bash
uv run pytest src/tests/path/to/test_file.py -q --no-cov
make lint
make test
make check-all
make zizmor
make validate-examples validate-pep723
make js-install build js-test validate-asyncapi browser-test
make installed-test PYTHON_VERSION=3.12
make installed-test PYTHON_VERSION=3.12 LITESTAR_BOUNDARY=latest
make browser-test-installed PYTHON_VERSION=3.12
make docs docs-linkcheck
```

## References

- [Distribution lanes](references/distribution-lanes.md)
- [Workflow hardening](references/workflow-hardening.md)
- [CI supply-chain pattern](../../bundles/knowledge/patterns/ci-supply-chain.md)
- [Distribution & browser testing](../../bundles/knowledge/testing/distribution-and-browser.md)
- [Runtime & tooling gotchas](../../bundles/knowledge/gotchas/runtime-and-tooling.md)
- [Project workflow](../../bundles/knowledge/workflow.md)
- [Tech stack](../../bundles/product/tech-stack.md)
