---
type: Spec
flow_id: contract-ergonomics
title: OpenAPI Inheritance and Name-Based Contract References
description: Inherit document metadata and security schemes from Litestar's OpenAPI config, optionally derive WebSocket servers, accept names instead of JSON-pointer references, and replace the hard-to-read explicit-contract example.
state: completed
parent_prd: null
research: [research/contract-ergonomics_20261105.md]
plan_revision: 2
plan_commit: 36294c1
state_revision: 10
current_task: null
last_verified_checkpoint: 5678474
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T04:10:00Z
tags: [feature, openapi, ergonomics, contracts, docs]
---

# OpenAPI Inheritance and Name-Based Contract References

## 1. Specification & Context

Approved by the user on 2026-11-05. The binding decisions are in the **Review Outcome and Revised Proposal** section of [`research/contract-ergonomics_20261105.md`](research/contract-ergonomics_20261105.md). Where it differs from the earlier "Proposal" section of the same note, that section wins.

Code anchors:
- `src/litestar_asyncapi/config.py::AsyncAPIConfig`
- `src/litestar_asyncapi/asyncapi/datastructures.py::OperationDefinition`, `ChannelDefinition`
- `src/litestar_asyncapi/asyncapi/generator.py::AsyncAPIGenerator.build_asyncapi`, `_populate_operations`, `_validate_references`, `_merge_components`
- `src/litestar_asyncapi/spec/{info,security_scheme,server,reply}.py`
- `docs/examples/contracts.py`
- `docs/integrations/security-and-servers.md`, `docs/learn/*.md`

## 2. Requirements

- **R1. Metadata inheritance.**
  - When unset, `title`, `version`, `description`, `contact`, `license`, `terms_of_service` and `external_docs` come from `app.openapi_config`. Explicit values win. Tags are not inherited.
  - `inherit_openapi: bool = True` disables all inheritance.
  - The default title becomes the OpenAPI title. This is breaking and goes in the changelog and migration notes.
- **R2. Security scheme inheritance.**
  - OpenAPI security schemes map to AsyncAPI through one adapter, using the mapping table in the research note.
  - Unmappable types are skipped with a warning.
  - Requirements are not inherited.
  - A name that collides with a different configured scheme raises, naming both sources.
- **R3. Opt-in servers.**
  - `inherit_openapi_servers: bool = False`.
  - When enabled, absolute OpenAPI URLs map `http`→`ws` and `https`→`wss`. Derived servers bind only to WebSocket-sourced channels. Relative URLs are skipped.
- **R4. Reading OpenAPI safely.**
  - `app.openapi_config` is read lazily in the build.
  - `openapi_config=None` and a `components` list are handled without mutating the config.
  - `app.openapi_schema` and `to_openapi_schema()` are never used.
- **R5. Name-based references.**
  - `OperationDefinition.security` and `ChannelDefinition.servers` accept lists of names. A bare `str` in place of a list is rejected.
  - New `ReplyDefinition(channel, messages, address)` is resolved after operations are populated. Unknown names raise with the valid names listed, and a message must belong to the reply channel.
  - The existing object and `Reference` forms keep working.
- **R6. Examples and docs.**
  - The Learn example is a typed broker request/reply. Its reply channel has its own `send` operation.
  - The advanced example uses JWTAuth with its inherited scheme, `security=["BearerToken"]`, a trait shared by two operations, and a correlation ID.
  - Docs pages are updated, including the sentence about servers.
- **R7. Schema-name parity.** A test pins that AsyncAPI component schema names equal the names Litestar's OpenAPI gives the same Python types.
- **R8. Validation.** Every mapped security type and derived server is covered by the generated validation fixture under `make validate-asyncapi` for 3.0.0 and 3.1.0.

## 3. Requirement-to-Task Traceability Matrix

| Requirement | Tasks |
| --- | --- |
| R1 Metadata inheritance | t01 |
| R2 Security scheme inheritance | t02 |
| R3 Opt-in servers | t03 |
| R4 Reading OpenAPI safely | t01, t02, t03 |
| R5 Name-based references | t04 |
| R6 Examples and docs | t05 |
| R7 Schema-name parity | t05 |
| R8 Validation | t02, t03 |

## 4. Implementation Plan

- [x] [d2b8cd5] t01 — inherit document metadata from the OpenAPI config (tasks/t01-openapi-metadata.md)
- [x] [7c6e515] t02 — inherit security schemes through one adapter; validation fixture (tasks/t02-openapi-security.md)
- [x] [7b911dd] t03 — opt-in WebSocket servers derived from OpenAPI servers (tasks/t03-openapi-servers.md)
- [x] [cd01faa] t04 — name-based security, server and reply references (tasks/t04-name-references.md)
- [x] [5678474] t05 — readable contract examples, docs and schema-name parity (tasks/t05-examples-docs.md)

**Recovery checkpoint:** `make lint && make test && make validate-asyncapi && make docs` exits `0`.

## 5. Continuity Snapshot

- **State:** completed at `5678474`. `make lint`, `make type-check`, `make test` (316 passed, 97.04%), `make validate-asyncapi` (25 documents, including `openapi-3.0.0`/`openapi-3.1.0` and the new examples) and `make docs` exit `0`.
- **Discoveries:** the `jwt` extra joined the `tests` dependency group so tests and the docs example use real `JWTAuth`; non-bearer HTTP schemes are lowercased too; an `oauth2` scheme with no absolute-URL flow is skipped; schema-name parity with Litestar OpenAPI already held. Changelog and migration entries landed with each feature commit.
- **Key decisions:** the Review Outcome section of the research note.
