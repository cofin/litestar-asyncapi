---
type: Guide
title: Public-Seam TDD and Test Map
description: Canonical test-file map, public seams and red-capable focused runs for Python changes.
tags: [testing, tdd, pytest, seams]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: addopts
    resource: pyproject.toml::tool.pytest.ini_options
    title: Global coverage floor
  - id: disc
    resource: src/tests/integration/test_discovery.py
    title: Nested router discovery
  - id: plugin
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.get_asyncapi_schema
    title: Primary public seam
---

# Public-Seam TDD and Test Map

<!-- truth: start -->
- Focused runs: `uv run pytest <path>[::test] -q --no-cov`. Without `--no-cov` the global `--cov-fail-under=80` addopt makes any partial run exit 1.
- Test through public seams: `AsyncAPIPlugin.get_asyncapi_schema(app)`, `get_asyncapi_json(app)`, docs routes via `litestar.testing` clients, decorators, and `AsyncAPIConfig` contracts.
- Build a real `Litestar` app per test; never mock the generator, extractors or schema bridge under test.
- Tests are synchronous. The only shared fixture is `src/tests/integration/conftest.py`, which asserts unique discovered channel keys across the integration suite.
- Add tests to the canonical file for the module below; never create `test_*remediation*.py` or `test_*audit*.py`.
- Assert on emitted wire content (keys, `$ref` targets, bounds), not on nonempty output.
<!-- truth: end -->

## Red-capable reproduction

Use the focused command from [Project workflow](../workflow.md). It must fail before the fix and pass after. A focused run without `--no-cov` exits 1 regardless of assertions[^addopts], so it cannot distinguish red from green.

## Canonical test map

| Source module | Canonical tests |
| --- | --- |
| `asyncapi/generator.py` | `unit/test_generator.py`, `unit/test_generator_components.py`, `unit/test_traits.py` |
| `asyncapi/extractors/websocket.py` | `unit/extractors/test_*inference.py`, `test_decorator_overrides.py`, `test_handler_metadata.py`, `test_docstring_descriptions.py`, `test_plain_websocket_fallback.py`, `integration/test_discovery.py` |
| `asyncapi/extractors/channels.py` | `unit/extractors/test_channels_plugin.py` |
| `asyncapi/datastructures.py` | `unit/extractors/test_datastructures.py` |
| `asyncapi/schema_generation/`, `_compat.py` | `unit/schema_generation/test_native.py`, `test_dialect.py` |
| `asyncapi/utils/examples.py` | `unit/utils/test_examples.py`, `unit/extractors/test_example_generation.py`, `test_example_precedence.py` |
| `spec/` | `unit/spec/test_base.py`, `test_asyncapi.py`, `test_wire_contract.py` |
| `decorators.py` | `unit/test_decorators.py` |
| `config.py` | `unit/test_config.py` |
| `plugins/`, `docs.py` | `unit/plugins/`, `unit/test_ui_security.py`, `unit/test_json_plugin.py`, `integration/test_routes.py`, `integration/test_plugin_cache.py` |
| `cli.py` | `integration/test_cli.py` (fixture app `fixtures/apps/cli.py`) |

Paths are relative to `src/tests/`.

## Dependency categories

- **In-process:** generator, extractors, spec models, dialect adapter. Exercise directly.
- **Local-substitutable:** Litestar app, `ChannelsPlugin` with the memory backend, `litestar.testing` clients. Use real instances.
- **External boundary:** official AsyncAPI parser/schemas and browsers. Covered by `make validate-asyncapi` and Playwright, never mocked in Python.

## Discovery coverage

Discovery tests cover root routes, nested routers and deeply nested routers, verifying cumulative paths and layered `include_in_schema` at every level[^disc].

[^addopts]: `pyproject.toml::tool.pytest.ini_options`
[^disc]: `src/tests/integration/test_discovery.py`
[^plugin]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.get_asyncapi_schema`
