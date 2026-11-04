---
name: review-asyncapi-generation
description: Use when reviewing diffs that touch litestar-asyncapi document assembly or discovery — asyncapi/generator.py, asyncapi/extractors/*, asyncapi/datastructures.py, decorators.py, AsyncAPIConfig contract fields in config.py, spec/** wire models, cli.py export, or their tests under src/tests/unit and src/tests/integration.
---

# Review: AsyncAPI Generation & Discovery

Zero-context review lens for the generation domain. Load [asyncapi-generation](../asyncapi-generation/SKILL.md) for the invariants this lens enforces.

## Scope

- `src/litestar_asyncapi/asyncapi/generator.py`, `asyncapi/extractors/`, `asyncapi/datastructures.py`, `asyncapi/utils/docstrings.py`
- `src/litestar_asyncapi/decorators.py`, `src/litestar_asyncapi/cli.py`, `src/litestar_asyncapi/config.py::AsyncAPIConfig`
- `src/litestar_asyncapi/spec/**`
- Matching tests in `src/tests/unit/` and `src/tests/integration/`

Route schema-conversion findings (`schema_generation/`, `_compat.py` schema creator, Draft07 dialect) to the asyncapi-schema review lens, and docs routing/renderer findings to the docs-UI lens.

## Procedure

1. Read the exact diff range and every changed function in full, plus its callers inside `build_asyncapi`.
2. Walk [checklist.md](references/checklist.md) `GEN-01..GEN-16` against each hunk. A rule applies only when the hunk touches its anchor or the data that flows through it.
3. Before recording a finding, check [false-positive-suppressions.md](references/false-positive-suppressions.md). A matching `FP-GEN-NN` suppresses the finding.
4. Confirm each finding with a concrete input: an app/handler/config that produces wrong output, a crash, or a silently weakened contract. Drop findings you cannot make concrete.
5. Check test evidence: the change needs a behavior test through `AsyncAPIGenerator(...).build_schema()`, a decorator, or `AsyncAPIConfig`, in the canonical test file for that seam, plus a negative test for every new raise path.

## Output format

One entry per finding, most severe first:

```text
[GEN-NN] <severity: high|medium|low> <path>:<line>
Summary: <one sentence defect>
Failure scenario: <concrete app/config input> -> <wrong document, crash, or lost contract>
Fix direction: <one sentence>
```

Severity: **high** = invalid or silently wrong wire document, lost explicit user contract, or nondeterminism; **medium** = missing conflict detection, missing negative test, convention break with runtime effect; **low** = test placement, naming, docstring accuracy.

End with `No findings` when nothing survives verification. Do not restate suppressed patterns.
