---
type: Pattern
title: CI Supply-Chain Hardening
description: GitHub Actions pinning, permissions and tested-artifact handoff rules audited by zizmor.
tags: [patterns, ci, github-actions, zizmor, supply-chain]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: ci
    resource: .github/workflows/ci.yml
    title: CI entry workflow
  - id: dist
    resource: .github/workflows/distribution.yml
    title: Reusable tested-distribution workflow
  - id: pub
    resource: .github/workflows/publish.yml
    title: PyPI trusted publishing
  - id: zizmor
    resource: Makefile::zizmor
    title: Workflow audit target
---

# CI Supply-Chain Hardening

<!-- truth: start -->
- Pin every external action to a full 40-character commit SHA with a trailing version comment.
- Declare minimal `permissions:` at workflow and job level; `id-token: write` only on publish/deploy jobs.
- `actions/checkout` always sets `persist-credentials: false`.
- Publishing downloads the wheel/sdist built and tested by `distribution.yml`; it never rebuilds.
- Call local reusable workflows through the self-repository form, not `./` relative paths.
- `make zizmor` reports zero high/medium findings.
<!-- truth: end -->

## Tested-artifact handoff

`distribution.yml` is a `workflow_call` workflow that runs `make js-install`, `make build js-test validate-asyncapi browser-test`, then installed-wheel Python and browser lanes[^dist]. CI calls it for every change[^ci]; `publish.yml` calls it again and publishes the uploaded artifact through PyPI trusted publishing in the `pypi` environment[^pub].

Anti-pattern: a publish job that runs `uv build`. Reason: the shipped wheel would differ from the one that passed browser and installed-wheel gates.

## Audit

`make zizmor` runs `uvx zizmor .github/workflows`[^zizmor]; CI runs it in the `prek` job alongside `validate-examples` and `validate-pep723`.

[^ci]: `.github/workflows/ci.yml`
[^dist]: `.github/workflows/distribution.yml`
[^pub]: `.github/workflows/publish.yml`
[^zizmor]: `Makefile::zizmor`
