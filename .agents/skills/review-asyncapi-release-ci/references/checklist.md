---
type: Checklist
title: "Release & CI Review Checklist"
description: Review rules for the asyncapi-release-ci domain.
tags: [skills, review-asyncapi-release-ci, checklist]
---

# Release & CI Review Checklist

## REL-01 **External Actions pin a full 40-character SHA with a version comment.**
Why: Tags are mutable; a retagged Action runs arbitrary code with job permissions.
Check: Every `uses: owner/repo@...` outside `$/` references a 40-hex SHA followed by `# vX`.
Anchor: `.github/workflows/*.yml::jobs.*.steps[].uses`

## REL-02 **Workflows default to read-only and elevate per job.**
Why: Top-level write scopes leak to every job, including untrusted PR code.
Check: Top-level `permissions: contents: read`; `id-token`, `pages`, or write scopes appear only on the job that needs them.
Anchor: `.github/workflows/publish.yml::jobs.pypi.permissions`, `.github/workflows/docs.yml::jobs.deploy.permissions`

## REL-03 **Checkout steps set `persist-credentials: false`.**
Why: Persisted tokens in `.git/config` are readable by later steps and uploaded artifacts.
Check: Each `actions/checkout` step has `with.persist-credentials: false`.
Anchor: `.github/workflows/*.yml::actions/checkout`

## REL-04 **Publishing consumes the tested distribution artifact.**
Why: Rebuilding in the publish job ships bytes no test lane exercised.
Check: `publish.yml::pypi` downloads `tested-distribution`; no `uv build`, `make build`, or checkout in that job.
Anchor: `.github/workflows/publish.yml::jobs.pypi`, `.github/workflows/distribution.yml::upload-artifact`

## REL-05 **Local reusable workflows use the self-repository reference.**
Why: Mixed reference styles break `workflow_call` resolution and zizmor auditing.
Check: Calls to `distribution.yml`/`test.yml` use `uses: $/.github/workflows/<file>.yml`.
Anchor: `.github/workflows/ci.yml::jobs.distribution`, `.github/workflows/publish.yml::jobs.distribution`

## REL-06 **Workflow inputs and contexts reach shell through `env`, not inline expressions.**
Why: `${{ }}` interpolated into `run:` is a template-injection vector.
Check: New `run:` lines reference `$VAR` set in `env:`; zizmor reports no `template-injection`.
Anchor: `.github/workflows/test.yml::jobs.test.env`

## REL-07 **CI steps call Makefile targets rather than duplicating recipes.**
Why: Divergent local and CI commands let a gate pass locally and fail in CI or the reverse.
Check: New gate logic lives in a `Makefile` target; workflows invoke `make <target>`.
Anchor: `Makefile::lint`, `.github/workflows/ci.yml::jobs.prek`

## REL-08 **The runtime Litestar dependency stays `>=2.24.0` without an upper cap, and boundaries move together.**
Why: A cap blocks downstream upgrades; a raised floor without updated `installed-test` pins leaves the minimum untested.
Check: `project.dependencies` floor equals `installed-test` `litestar==` pin and the `minimum` assertion.
Anchor: `pyproject.toml::project.dependencies`, `Makefile::installed-test`

## REL-09 **`installed-test` proves imports come from site-packages outside the checkout.**
Why: Running inside the checkout imports `src/` and hides missing package data.
Check: The temp-workdir copy, `is_relative_to(sys.prefix)` assertion and `--no-cov` run remain intact.
Anchor: `Makefile::installed-test`

## REL-10 **Packaged assets stay complete in wheel and sdist.**
Why: A missing hashed bundle or license renders a blank docs page for every consumer.
Check: `tool.hatch.build.targets.{wheel,sdist}.artifacts` include `src/litestar_asyncapi/assets/**`; `make build` still runs `distribution.py`; manifest and committed files change together.
Anchor: `pyproject.toml::tool.hatch.build`, `tools/frontend/tests/distribution.py::check_assets`, `vite.config.ts::build`

## REL-11 **Frontend dependencies are exact and locked.**
Why: Ranges in `package.json` drift the packaged UI and the official validator between builds.
Check: `devDependencies` use exact versions; `package-lock.json` changes accompany `package.json` changes; CI installs via `make js-install` (`npm ci`).
Anchor: `package.json::devDependencies`, `Makefile::js-install`

## REL-12 **New or replacement gates are proven against an isolated violation.**
Why: A gate that never fails (wrong glob, swallowed exit code) gives false assurance.
Check: The change description or test shows the gate rejecting a deliberate violation; recipes keep `set -eu`/`-euo pipefail` semantics and do not append `|| true` to gate commands.
Anchor: `Makefile::SHELLFLAGS`, `tools/validate_asyncapi.mjs::rejection`

## REL-13 **Focused test commands disable the global coverage floor.**
Why: `--cov-fail-under=80` in addopts makes any partial run exit 1 even when tests pass.
Check: Documented or scripted single-file runs use `--no-cov`; full-suite coverage stays in `make test`/`make coverage`.
Anchor: `pyproject.toml::tool.pytest.ini_options.addopts`

## REL-14 **Release automation never tags, commits or pushes on its own.**
Why: Tags trigger publication; unattended tagging ships unreviewed versions.
Check: `tool.bumpversion` keeps `commit = false` and `tag = false`; no target or workflow adds `git tag`, `git push`, or `gh release create`.
Anchor: `pyproject.toml::tool.bumpversion`, `Makefile::release`, `Makefile::pre-release`

## REL-15 **Runnable doc examples keep valid PEP 723 metadata and standalone marker blocks.**
Why: Broken metadata or marker blocks break copy-paste examples and CI.
Check: `# /// script` with `requires-python >=3.11` and a `litestar-asyncapi` dependency; a module-level `app` that serves its document.
Anchor: `tools/ci/validate_pep723_blocks.py::validate_file`, `src/tests/unit/docs/test_examples.py`

## REL-16 **Python code stays free of `from __future__ import annotations`, and package code free of inline comments.**
Why: Future annotations break Litestar runtime signature introspection; inline comments violate project style.
Check: `__future__.annotations` stays in ruff's `banned-api` and no per-file ignore disables TID251; new tooling Python uses docstrings instead of `#` comments.
Anchor: `pyproject.toml::tool.ruff.lint.flake8-tidy-imports.banned-api`
