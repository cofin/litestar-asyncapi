---
name: asyncapi-generation
description: Use when changing AsyncAPI document assembly or discovery in litestar-asyncapi — asyncapi/generator.py (AsyncAPIGenerator, _ensure_unique_operation_id, _normalize_channels, _validate_references), extractors/websocket.py or channels.py, datastructures.py (MessageDefinition, OperationDefinition, ChannelDefinition), decorators.py (asyncapi_operation, asyncapi_message), AsyncAPIConfig contract fields, spec/** wire models and BaseSchemaObject.to_schema, or cli.py asyncapi export.
---

# AsyncAPI Generation & Discovery

<!-- truth: start -->
- `AsyncAPIGenerator.build_asyncapi` is the single assembly path: discover → `_normalize_channels` → `_populate_channels` → `_populate_operations` → merge schema components → `_validate_references`. Add behavior inside this pipeline, not beside it.
- Operation identity is the `document.operations` map key. Never emit a wire `operationId` property.
- Operation keys and ids are unique case-insensitively via `.casefold()`. `strict_uniqueness=True` raises `ImproperlyConfiguredException`; otherwise suffix `_2`, `_3`, ….
- Every generated `$ref` token passes through `_json_pointer_escape` (RFC 6901 `~`→`~0`, `/`→`~1`, then percent-quoting).
- `MessageDefinition`, `OperationDefinition`, `ChannelDefinition` are the shared typed contract for decorators, extractors and `AsyncAPIConfig.channels`. `DiscoveredOperation`/`DiscoveredChannel` add provenance only.
- Python payload/header types survive until `_build_message`; extractors never pre-render schemas except ChannelsPlugin's unconstrained `Schema()`.
- `None` means "no override"; an explicit empty list (`messages=[]`, `examples=[]`) is an override.
- Explicit `ChannelDefinition.key` replaces matching inferred channels; duplicate explicit keys raise with both sources. Inferred channels merge only when they share the same `route_identity` object and address.
- Conflicts (channel, message, component, trait) raise `ImproperlyConfiguredException` naming both provenance strings. Never silently pick one side.
- Ordering is deterministic through `_definition_key` (public values, never `id()`); keep provenance/route_identity out of ordering keys.
- `include_in_schema` in handler `opt` is honored by both extractors (`_should_include_handler`).
- Raw `@websocket` handlers emit nothing unless decorated or `include_raw_websocket_routes=True`, which emits placeholders with a `UserWarning`.
- ChannelsPlugin-generated routes are discovered only by `extract_channels_plugin_channels` (send-only); `extract_websocket_channels` skips them via `generated_channels_mode`.
- AsyncAPI 3 `Parameter` carries no nested schema; type information goes in `description`.
- Spec models subclass `BaseSchemaObject`, are `@dataclass(slots=True)`, and serialize through `to_schema`: `UNSET` (Litestar `Empty`) omits; `None` omits unless field metadata `nullable=True`; `extensions` keys must start with `x-` and never shadow modeled fields.
- Logical `content_type` is distinct from the `x-websocket-mode` frame-mode extension; explicit extensions win over inferred ones.
- Private Litestar imports live only in `_compat.py`; extractors call its helpers (`websocket_signature`, `websocket_payload`, `generated_channels_mode`).
- Python >=3.10, PEP 604/585 typing, no inline comments (Google docstrings), owned classes slotted.
- Focused tests: `uv run pytest <path> -q --no-cov` (the global coverage floor fails focused runs).
<!-- truth: end -->

## Scope

- `src/litestar_asyncapi/asyncapi/generator.py`
- `src/litestar_asyncapi/asyncapi/extractors/websocket.py`, `extractors/channels.py`
- `src/litestar_asyncapi/asyncapi/datastructures.py`, `asyncapi/utils/docstrings.py`
- `src/litestar_asyncapi/decorators.py`, `src/litestar_asyncapi/cli.py`
- `src/litestar_asyncapi/config.py::AsyncAPIConfig` (contract fields; `DocsConfig` belongs to the docs-UI domain)
- `src/litestar_asyncapi/spec/**` (wire models, `bindings/`)
- Tests: `src/tests/unit/test_generator*.py`, `test_operation_id_hardening.py`, `test_traits.py`, `test_decorators*.py`, `test_config.py`, `unit/extractors/*`, `unit/spec/*`, `src/tests/integration/{test_discovery,test_routes,test_cli,test_asyncapi_metadata_examples}.py`

Schema conversion (`asyncapi/schema_generation/`, `_compat.py` schema creator, examples) belongs to the asyncapi-schema domain; consume it through `AsyncAPISchemaGenerator.generate/components/declared_examples`.

## Seams

| Role | Element |
| --- | --- |
| Module | Document generation: route/config contracts in, `AsyncAPI` wire model out |
| Interface | `AsyncAPIGenerator(app, config).build_asyncapi()` / `.build_schema()`; public contract types `MessageDefinition`, `OperationDefinition`, `ChannelDefinition`; decorators `asyncapi_operation`, `asyncapi_message`; `AsyncAPIConfig` |
| Implementation | Private `_discover_channels`, `_normalize_channels`, `_populate_*`, `_build_message`, `_definition_key`, `_reference_index`, `_validate_references` |
| Seam | `AsyncAPIConfig` flags and `channels`; handler `opt["asyncapi"]` (`ASYNCAPI_OPT_KEY`) carrying `AsyncAPIMetadata`; `AsyncAPISchemaGenerator` |
| Adapter | `_compat.py` helpers translating Litestar private handler signatures; `BaseSchemaObject.to_schema` translating Python models to wire dicts |

Dependency categories:

1. **In-process** — spec models, datastructures, `_definition_key`; test directly.
2. **Local-substitutable** — a real `Litestar(...)` app with real handlers and `ChannelsPlugin`; construct one per test instead of mocking routes.
3. **Remote-owned** — Litestar internals behind `_compat.py`; supported range `litestar>=2.24.0` (no upper cap; CI exercises 2.24.0 and latest).
4. **External boundary** — filesystem/stdout in `cli.py export`; exercise through Click's runner in `test_cli.py`.

## Workflow

1. Classify the change: discovery (extractors), contract shape (datastructures/decorators/config), assembly/identity (generator), or wire serialization (spec). Read [contracts-and-discovery](references/contracts-and-discovery.md) or [assembly-and-identity](references/assembly-and-identity.md).
2. Write the failing test first in the canonical file for that seam (see the test map in the references), driving through `AsyncAPIGenerator(app, config).build_schema()` or the decorator/config public API.
3. Implement in the owning function. New contract fields go on the shared definition dataclass and must flow through `_apply_decorator_overrides`, `_discover_channels` field copying, `_build_message`, and `_definition_key` stability.
4. For any new `$ref`, escape every token and confirm `_validate_references` accepts the target kind and location.
5. For any new conflict, raise `ImproperlyConfiguredException` naming both provenance strings; add a negative test.
6. Run the focused test, then the gates below.

## Verification

```bash
uv run pytest src/tests/unit/test_generator.py -q --no-cov
uv run pytest src/tests/unit/extractors -q --no-cov
uv run pytest src/tests/integration/test_discovery.py -q --no-cov
make type-check
make slotscheck
make lint
make test
make check-all
```

Wire-contract changes also need the official schema gate: `make validate-asyncapi` (Node (`.nvmrc`)).

## References

- [Contracts & discovery](references/contracts-and-discovery.md)
- [Assembly & identity](references/assembly-and-identity.md)
- [Architecture 02: Generator pipeline](../../bundles/knowledge/architecture/02-generator-pipeline.md)
- [Architecture 03: Discovery & extractors](../../bundles/knowledge/architecture/03-discovery-and-extractors.md)
- [Architecture 05: Spec objects & serialization](../../bundles/knowledge/architecture/05-spec-objects-and-serialization.md)
- [Patterns: schema generation](../../bundles/knowledge/patterns/schema-generation.md)
- [Domain: AsyncAPI contracts](../../bundles/knowledge/domains/asyncapi-contracts.md)
- [Testing: public-seam TDD](../../bundles/knowledge/testing/public-seam-tdd.md)
- [Gotchas: runtime & tooling](../../bundles/knowledge/gotchas/runtime-and-tooling.md)
