---
type: Suppressions
title: "Release & CI False-Positive Suppressions"
description: Intentional asyncapi-release-ci patterns reviewers must not flag.
tags: [skills, review-asyncapi-release-ci, false-positive-suppressions]
---

# Release & CI False-Positive Suppressions

Intentional repository patterns. Drop a candidate finding that matches one of these.

## FP-REL-01 Uncapped runtime Litestar dependency with a capped `latest` test boundary
`pyproject.toml::project.dependencies` is `litestar>=2.24.0`, while `Makefile::installed-test` uses `litestar>=2.24,<3` for `LITESTAR_BOUNDARY=latest`.
DO NOT FLAG: the cap bounds what CI claims to have tested; the uncapped runtime floor keeps downstream resolution unblocked.

## FP-REL-02 Node is required only for build and test
`package.json` is `private`, pins `engines.node: 22.x`, and holds only `devDependencies`.
DO NOT FLAG missing runtime Node/npm requirements or absent Python-side JS dependencies: the wheel ships prebuilt assets.

## FP-REL-03 Built UI assets are committed
`src/litestar_asyncapi/assets/ui/**` (hashed JS/CSS, `manifest.json`, `THIRD-PARTY-LICENSES.md`) is tracked and excluded from prek (`.pre-commit-config.yaml::exclude`).
DO NOT FLAG generated or minified files in the diff, their lint exclusion, or large hashed-file churn after a frontend bump.

## FP-REL-04 Publish job downloads instead of building
`publish.yml::pypi` has no checkout and no build step; it downloads `tested-distribution`.
DO NOT FLAG "missing build" or "missing checkout": publishing the tested bytes is the contract.

## FP-REL-05 `$/` reusable workflow references
`uses: $/.github/workflows/distribution.yml` and `.../test.yml` are the self-repository form.
DO NOT FLAG as a typo or as an unpinned reference.

## FP-REL-06 prek hooks pin by `rev` tag
`.pre-commit-config.yaml` uses `rev: vX.Y.Z` and updates through `make upgrade` with a 7-day cooldown.
DO NOT FLAG under REL-01: SHA pinning applies to GitHub Actions; hook revisions run locally and in the read-only lint job.

## FP-REL-07 Coverage only on one matrix cell
`ci.yml::test_python` sets `coverage` true only for Python 3.12 with `minimum`.
DO NOT FLAG missing coverage on other cells: they run `installed-test` with `--no-cov` against the installed wheel.

## FP-REL-08 `--no-cov` in `installed-test`
The installed lane runs `pytest tests --no-cov -q` outside the checkout.
DO NOT FLAG as bypassing the coverage gate: coverage of the installed package path is not comparable to `src/` coverage, and the floor is enforced by `make test`/`make coverage`.

## FP-REL-09 `release` target help text mentions a tag
`Makefile::release` help says "create release tag" while `tool.bumpversion` sets `tag = false`.
DO NOT FLAG as unintended tagging: no tag is created; the GitHub release is made manually by the maintainer.

## FP-REL-10 Broad ruff per-file ignores for tests, tools and docs
`pyproject.toml::tool.ruff.lint.per-file-ignores` relaxes `S`, `D`, `T201`, `PLR2004`, etc. for `src/tests/**`, `tools/**/*.py`, and `docs/**/*.py`.
DO NOT FLAG: assertions, prints, subprocesses and missing docstrings are expected in tests, scripts and examples.

## FP-REL-11 Slotscheck class exclusions
`tool.slotscheck.exclude-classes` excludes `spec.bindings.*Binding` and `plugins.renderers:AsyncAPIUIRenderPlugin`.
DO NOT FLAG: the renderer inherits Litestar's unslotted native base, and duplicating that base to satisfy slotscheck is worse.
