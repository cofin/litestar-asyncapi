---
type: Reference
title: "Workflow Hardening"
description: Workflow Hardening reference for the asyncapi-release-ci skill.
tags: [skills, asyncapi-release-ci, workflow-hardening]
---

# Workflow Hardening

Supply-chain rules for `.github/workflows/*.yml`, audited by `make zizmor` (`uvx zizmor .github/workflows`).

## Pinning

- Pin every external Action to a full 40-character commit SHA with a trailing version comment:
  `uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`.
- Update a pin by resolving the new tag to its commit SHA and replacing both SHA and comment in every workflow that uses the Action.
- prek hooks in `.pre-commit-config.yaml` pin by `rev:` tag and update through `make upgrade` (`uvx prek autoupdate --cooldown-days 7`).

## Permissions

- Each workflow declares top-level `permissions: contents: read`.
- Elevate only on the job that needs it:
  - `publish.yml::pypi`: `id-token: write`, `environment: pypi`.
  - `docs.yml::deploy`: `pages: write`, `id-token: write`, `environment: github-pages`.
  - `pr-title.yml`: `pull-requests: read`.
- Secrets reach only the step that consumes them (`CODECOV_TOKEN` in `ci.yml::codecov`, `GITHUB_TOKEN` in `pr-title.yml`).

## Checkout

Every `actions/checkout` step sets:

```yaml
with:
  persist-credentials: false
```

`publish.yml::pypi` has no checkout; it consumes only the downloaded artifact.

## Reusable workflows

- Shared lanes are `on: workflow_call` (`distribution.yml`, `test.yml`).
- Call them with the self-repository form `uses: $/.github/workflows/<file>.yml`.
- Pass matrix values as typed `inputs` (`python-version`, `litestar-boundary`, `coverage`, `timeout`) and map them to `env` before use in `run:` so expressions never interpolate into shell text.

## Artifact handoff

- `distribution.yml` uploads `dist/*` as `tested-distribution` with `if-no-files-found: error` after build, Vitest, official validation, Playwright and installed checks.
- Consumers download into `dist` and run `make installed-test` or publish directly. Do not add `uv build` or `make build` to consumer jobs.

## Concurrency and timeouts

- `ci.yml` uses `concurrency.group: test-${{ github.head_ref || github.ref }}` with `cancel-in-progress: true`.
- `distribution.yml` sets `timeout-minutes: 30`; `test.yml` takes `timeout` as input.

## Verification

```bash
make zizmor
uvx prek run check-yaml --all-files
```
