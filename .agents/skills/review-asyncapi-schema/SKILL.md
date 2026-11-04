---
name: review-asyncapi-schema
description: Use when reviewing diffs that touch litestar-asyncapi schema generation or examples — src/litestar_asyncapi/_compat.py, asyncapi/schema_generation/{schema,dialect}.py, asyncapi/utils/examples.py, spec/schema.py, _build_message in generator.py, or their tests under src/tests/unit/schema_generation and test_examples.py — to catch Draft07 wire regressions, registry leaks, lost null presence and example-precedence bugs.
---

# Review: AsyncAPI Schema Generation

## Scope

Apply this lens to changes in:

- `src/litestar_asyncapi/_compat.py` (schema, example and DTO helpers)
- `src/litestar_asyncapi/asyncapi/schema_generation/schema.py`, `dialect.py`
- `src/litestar_asyncapi/asyncapi/utils/examples.py`
- `src/litestar_asyncapi/spec/schema.py`
- `src/litestar_asyncapi/asyncapi/generator.py::_build_message`, `AsyncAPIGenerator.build_asyncapi` (components merge)
- `src/tests/unit/schema_generation/`, `src/tests/unit/utils/test_examples.py`, `src/tests/unit/extractors/test_example_*.py`, `tools/validate_asyncapi.mjs`

Load [`../asyncapi-schema/SKILL.md`](../asyncapi-schema/SKILL.md) for invariants and seams before judging a change.

## Procedure

1. Read the full diff and the touched functions in their current form; resolve each changed line to its owning seam (native bridge, registry, dialect, examples).
2. Walk every rule in [`references/checklist.md`](references/checklist.md). For each candidate finding, construct a concrete input (annotation, schema dict or config) and the wrong wire output or crash it produces. Drop candidates without a concrete failure scenario.
3. Check each surviving candidate against [`references/false-positive-suppressions.md`](references/false-positive-suppressions.md). Drop any that match an `FP-SCH` entry.
4. When a finding is about missing coverage, name the canonical test file and the public call (`AsyncAPISchemaGenerator.generate`, `to_asyncapi_schema`, `generate_example`) that would expose it.
5. Optionally confirm with `uv run pytest <path> -q --no-cov` or `make validate-asyncapi`; report whether evidence was executed or reasoned.

## Output Format

One entry per finding, most severe first:

```text
[SCH-NN] <severity: critical|high|medium|low> <path>:<line>
Defect: <one sentence>
Failure scenario: <concrete input> -> <wrong output / exception>
Fix direction: <one sentence, owning file>
Evidence: executed <command> | reasoned
```

Severity: **critical** = invalid or semantically weaker wire contract emitted silently; **high** = crash or wrong schema for a supported type; **medium** = lost context, precedence or isolation defect; **low** = coverage or style rule. Report "No SCH findings" when nothing survives.

## References

- [Checklist SCH-01..16](references/checklist.md)
- [False-positive suppressions FP-SCH-01..09](references/false-positive-suppressions.md)
- [Draft07 dialect export](../asyncapi-schema/references/draft07-dialect.md)
- [Native bridge, registry and examples](../asyncapi-schema/references/native-bridge.md)
