---
type: Research
research_id: "codebase-audit-20261104"
title: "Primary-Source Audit: Codebase Health, AsyncAPI Conformance and Roadmap"
description: "Baseline gates are green apart from a codespell false positive; four wire-contract bugs, four discovery/routing bugs and an AsyncAPI 3.x feature-gap list are verified and ranked."
scope: architecture
status: stable
state: promoted
promoted_to: contract-fixes
tags: [research, audit, asyncapi, conformance, schema, generation, docs-ui]
generated:
  by: flow/0.26.0
  at: 2026-11-04T00:00:00Z
verified:
  - by: agent:researcher
    at: 2026-11-04T00:00:00Z
  - by: agent:asyncapi-generation-reviewer
    at: 2026-11-04T00:00:00Z
  - by: agent:asyncapi-schema-reviewer
    at: 2026-11-04T00:00:00Z
  - by: agent:asyncapi-docs-ui-reviewer
    at: 2026-11-04T00:00:00Z
sources:
  - id: base-normalize
    resource: src/litestar_asyncapi/spec/base.py::_normalize_key
    title: Wire key normalization
  - id: kafka-bindings
    resource: src/litestar_asyncapi/spec/bindings/kafka.py::KafkaServerBinding
    title: Kafka binding models
  - id: ws-extractor
    resource: src/litestar_asyncapi/asyncapi/extractors/websocket.py::_infer_operations_from_handler
    title: WebSocket operation inference
  - id: docs-router
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.create_docs_router
    title: Docs router construction
  - id: schema-creator
    resource: src/litestar_asyncapi/_compat.py::_SchemaCreator
    title: Native schema creator overrides
  - id: wire-schema
    resource: src/litestar_asyncapi/spec/schema.py::Schema
    title: Draft07 wire schema model
  - id: validator
    resource: tools/validate_asyncapi.mjs
    title: Official validator gate
  - id: spec-310-notes
    resource: https://www.asyncapi.com/blog/release-notes-3.1.0
    title: AsyncAPI 3.1.0 release notes
  - id: spec-releases
    resource: https://github.com/asyncapi/spec/releases
    title: AsyncAPI specification releases
  - id: spec-json-schemas
    resource: https://github.com/asyncapi/spec-json-schemas/releases
    title: Official AsyncAPI JSON schemas (6.11.1)
---

# Primary-Source Audit: Codebase Health, AsyncAPI Conformance and Roadmap

Audit of `feat/updates-1` at `23d1a4a`. Severity: **Critical** breaks valid users today; **Important** emits a wrong contract or wrong page for a supported configuration; **Minor** is an edge case or precedence slip; **Cleanup** is dead or redundant code.

## Baseline Gates

- `uv run pytest`: 212 passed, 93.35% coverage. `make type-check`: mypy and pyright clean.
- `make lint` fails at codespell. The hook flags the pytest key `addopts` (as `addopt`) in four `.agents/` documents. Add `addopt` to `pyproject.toml::tool.codespell.ignore-words-list`. Lint steps after prek do not run until this passes.
- `pyproject.toml::tool.mypy` sets `warn_untyped_fields`, which pydantic-mypy rejects as an unrecognized option.
- A strict Sphinx build (`-W`, empty `suppress_warnings`) emits zero warnings.

## Verified Bugs

Every row was reproduced by running code against HEAD. Repro scripts are kept outside the repository.

| ID | Severity | Location | Failure |
| --- | --- | --- | --- |
| B1 | Important | `spec/base.py::_normalize_key` | The `schema_` prefix strip runs before camelCasing. `KafkaServerBinding` emits `registry_url`/`registry_vendor` and `KafkaMessageBinding` emits `id_location`/`id_payload_encoding`/`lookup_strategy`. The official kafka 0.5.0 binding schemas set `additionalProperties: false`, so documents that use these bindings fail validation. |
| B2 | Important | `extractors/websocket.py::_infer_operations_from_handler` | Every `@websocket_listener` gets the operation id `ListenerHandler_receive`/`_send`, numbered `_2`, `_3` by route order, because the id comes from Litestar's wrapper class. `strict_uniqueness=True` then raises on any app with two listeners. `src/tests/integration/test_cli.py` asserts the wrong key. The same root cause affects the decorator error text in `decorators.py` and the provenance string in `extractors/channels.py`. |
| B3 | Important | `plugins/core.py::AsyncAPIPlugin.create_docs_router` | Route names are global constants. With two `AsyncAPIPlugin` instances, `url_for` resolves to whichever registered first. One docs page then loads the other's document and assets, and a guarded internal document can appear on a public page. |
| B4 | Important | `_compat.py::_SchemaCreator.for_field_definition` | `Annotated[tuple[int, ...], Parameter(max_items=3)]` yields `items: {oneOf: [{type: integer}, {}]}`, so the item type is lost. |
| B5 | Important | `_compat.py::_SchemaCreator` | Zero bounds (`max_items=0`, `max_length=0`) are dropped because native Litestar tests them for truthiness. Only fixed tuples are protected. |
| B6 | Important | `spec/schema.py::Schema.prefix_items` | Explicit wire `Schema` objects emit the 2020-12 keyword `prefixItems` into Draft07 documents. Validators ignore it, so positional typing disappears without any error. |
| B7 | Minor | `extractors/websocket.py::_apply_decorator_overrides` | Handler `opt` metadata and docstrings are applied before decorator overrides, so operations that a decorator adds lose their summary and description. |
| B8 | Minor | `decorators.py::asyncapi_operation`, `asyncapi_message` | Decorator stacking order changes the result. `messages=` replaces messages added by `asyncapi_message` and skips the duplicate-name check. |
| B9 | Minor | `_compat.py::declared_schema_examples` | Declared model examples are ignored behind `Optional[P]`, so a random example wins. |
| B10 | Minor | `generator.py::_build_message` | With a string payload annotation and `signature_namespace`, the schema resolves but example generation fails with "Unsupported type". |
| B11 | Minor | `_compat.py::_SchemaCreator.process_schema_result` | For `Optional[int] = None`, the integer branch carries a contradictory `default: null`. |
| B12 | Minor | `config.py::DocsConfig`, `AsyncAPIConfig` | `DocsConfig(path="/")` turns the docs catch-all into the app's global 404 and puts the docs guards on it. `spec_version="3.0"` is accepted without validation. `OperationDefinition(action="Send")` raises, but the decorators accept it. |
| B13 | Minor | `tools/frontend/interactive.ts::supportsWire` | Payloads with `type: [object, null]` or a top-level `oneOf` of objects get "console unavailable". |

## Cleanup

- `generator.py::_normalize_channels`: the merge path is never reached by real discovery, which cannot produce two channels with the same route identity. It is reached only by two `test_generator.py` tests that monkeypatch the extractor.
- Redundant checks: `extract_websocket_channels` re-checks `config`/`include_websocket_routes`; `_path_parameters_to_parameters` has an unused `schema_generator` argument; the `Reference` guard in `_populate_channels` can never fire; `_is_none_return_type` has overlapping predicates; `_should_include_handler` checks `hasattr(handler, "opt")`.
- `plugins/core.py`: with `use_cache=False`, a freshly built document is deep-copied twice. The manifest is re-read from disk on every HTML request (`docs.py::bootstrap_html`). The per-request copy of the cached schema and `_cached_json` are load-bearing: the copy protects the cache from user render plugins, and `_cached_json` backs the public `get_asyncapi_json`.
- Schema error messages nest `500:` prefixes and full `ParameterKwarg` reprs. `components()` lists every payload origin instead of the one that failed.
- `spec/security_scheme.py` has an internal planning label in a code comment. `_normalize_key` renames any field ending in `_in` to `in`.
- The `asyncapi-schema` skill says Pydantic `prefer_alias` defaults to `True`. Litestar actually registers `PydanticSchemaPlugin(prefer_alias=False)`.

## Validation Coverage Gap

`tools/validate_asyncapi.mjs` runs the official AJV schemas and `@asyncapi/parser` only against the WebSocket and boolean fixtures plus the exported fixture. These cover security schemes, traits and `ws` bindings, but no Kafka or AMQP bindings and no `x-` extensions, so the gate could never have caught B1. A fixture covering those objects is the cheapest guard against this class of bug.

## AsyncAPI Conformance

- **Object coverage matches 3.x.** The models cover Server, ServerVariable, Channel, Parameter, Operation, OperationTrait, Message, MessageTrait, Reply, ReplyAddress, Components (all 19 maps), Tag, ExternalDocs, CorrelationId, MultiFormatSchema and Schema. `x-` extensions are allowed exactly where the spec allows them; MessageExample and Reference correctly reject them.
- **Parameters carry no schema.** This is correct for 3.x.
- **3.0 vs 3.1.** The two versions differ only in ROS 2 bindings, a looser `MessageExample.payload`, and one extra `schemaFormat` value. 3.1.0 is non-breaking, so switching only the version string is correct.
- **Newer versions.** As of 2026-11-04, 3.1.0 (2026-01-31) is the latest release, with no 3.2/4.0 or RC tags. Open topics are proposals only: out-of-sequence events (#1143), AND-combined security (#1129), discriminator alignment (#1073) and retry/dead-letter operations.

## Feature Gaps Worth Adding

1. **Info metadata in config.** `AsyncAPIConfig` cannot set `contact`, `license`, `termsOfService`, `tags`, `externalDocs`, the document `id` or root extensions, even though the wire models support all of them.
2. **Typed security.** Add `OAuthFlows`/`OAuthFlow` models (3.x uses `availableScopes`) in place of the untyped `flows` dict. Optionally map Litestar auth backends to `securitySchemes` and route guards to per-operation `security`.
3. **WebSocket channel bindings.** Derive the `ws` binding `query` and `headers` schemas from route parameters.
4. **Operation bindings.** Add operation-binding models for Kafka, AMQP and HTTP, plus multi-format/Avro pass-through helpers. Lower priority.

## Limitations

- B13 is from code reading only. All other bugs were reproduced.
- The conformance review read the bundled official JSON schemas (`@asyncapi/specs` 6.11.1) and the release notes, not the full prose of the specification.
- Statements about future spec versions reflect public GitHub state on 2026-11-04.
