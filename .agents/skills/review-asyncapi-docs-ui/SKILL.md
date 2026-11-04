---
name: review-asyncapi-docs-ui
description: Use when reviewing diffs that touch plugins/core.py, plugins/renderers.py, docs.py, DocsConfig, assets/bootstrap.js, assets/ui/**, tools/frontend/*.ts, vite.config.ts, playwright.config.ts or the docs route, cache, UI security and browser tests, to catch escaping gaps, native-renderer duplication, cache ownership leaks, interaction-boundary violations and stale packaged assets.
---

# Review: AsyncAPI Documentation Routes & Packaged UI

## Scope

Apply this lens to any change under:

- `src/litestar_asyncapi/plugins/**`, `src/litestar_asyncapi/docs.py`, `src/litestar_asyncapi/config.py::DocsConfig`
- `src/litestar_asyncapi/assets/**`
- `tools/frontend/**`, `vite.config.ts`, `playwright.config.ts`, `package.json`, `package-lock.json`
- `src/tests/unit/test_ui_security.py`, `src/tests/unit/test_json_plugin.py`, `src/tests/unit/plugins/**`, `src/tests/integration/test_routes.py`, `src/tests/integration/test_plugin_cache.py`

Load the engineering skill [`asyncapi-docs-ui`](../asyncapi-docs-ui/SKILL.md) for the invariants and seams.

## Procedure

1. Read the exact diff and every touched symbol's callers. Do not review from the summary.
2. Walk [references/checklist.md](references/checklist.md) rule by rule (`UI-01..UI-16`). Record a finding only with a concrete failure scenario: the input or state, and the wrong output, crash or exposure that results.
3. Before reporting, compare each candidate with [references/false-positive-suppressions.md](references/false-positive-suppressions.md). Drop any candidate that matches an `FP-UI-*` entry, unless the diff breaks that entry's stated precondition.
4. Check that tests changed together with the behavior, in the canonical files, through the public seam (`TestClient` routes, `AsyncAPIPlugin` accessors, exported TS functions, real Chromium).
5. When the diff touches `tools/frontend/**` or `vite.config.ts`, confirm that regenerated `assets/ui/**` is in the same change.

## Output Format

One entry per finding, most severe first:

```text
[UI-NN] path/to/file.py:LINE — severity: critical|high|medium|low
Defect: <one sentence>
Failure scenario: <concrete input/state -> wrong output/crash/exposure>
Fix direction: <one sentence, native seam first>
```

Severity guide: **critical** = XSS, guard bypass or cross-app document leak. **high** = wrong or missing contract in the rendered UI or downloads, or a broken installed wheel. **medium** = a missing hostile-input or browser regression, or duplicated native behavior. **low** = naming, docstrings or test placement.

When nothing survives the suppressions, write `No findings (UI checklist applied, N suppressions matched).`
