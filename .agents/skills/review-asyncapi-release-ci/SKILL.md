---
name: review-asyncapi-release-ci
description: Use when reviewing changes to Makefile, pyproject.toml build/test/lint/bumpversion config, package.json, package-lock.json, vite.config.ts, playwright.config.ts, .github/workflows/*.yml, .pre-commit-config.yaml, tools/ci/*.py, tools/validate_asyncapi.mjs, tools/docs/*.py, zensical.toml, committed assets under src/litestar_asyncapi/assets/ui/, or PEP 723 blocks in docs/examples.
---

# Review: AsyncAPI Release & CI

Zero-context review lens for build, packaging, CI and release surfaces. Load the engineering skill [asyncapi-release-ci](../asyncapi-release-ci/SKILL.md) for invariants and lane composition.

## Scope

Review only files in the description. Route Python library behavior to the generation, schema or docs-UI review skills.

## Procedure

1. Read the exact diff range and list touched lanes (static, source tests, packaged UI, official contract, browser, installed, docs, publish).
2. Apply every rule in [checklist.md](references/checklist.md) whose `Anchor:` intersects the diff.
3. Before reporting, match each candidate against [false-positive-suppressions.md](references/false-positive-suppressions.md); drop any that match an `FP-REL` entry.
4. For each surviving finding, construct a concrete failure scenario (input, command or event, and the wrong outcome). Drop findings without one.
5. Confirm with a read-only command when possible (`make zizmor`, `uvx prek run check-yaml --all-files`, `git diff --stat`), and cite its output.

## Output

One entry per finding, most severe first:

```text
[REL-NN] <severity: high|medium|low> path/to/file:line
Summary: <one sentence defect>
Failure scenario: <concrete trigger -> wrong outcome>
Evidence: <command output or quoted line>
```

End with `Lanes touched: ...` and `Rules applied: REL-..`. Report `No findings` when nothing survives.
