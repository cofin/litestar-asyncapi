---
type: Task
id: contract-ergonomics:t04
title: Name-based security, server and reply references
state: completed
priority: P1
verification_strategy: behavior_tdd
depends_on: [t03]
files:
  - docs/project/changelog.md
  - docs/reference/contracts.md
  - src/litestar_asyncapi/__init__.py
  - src/litestar_asyncapi/asyncapi/datastructures.py
  - src/litestar_asyncapi/asyncapi/generator.py
  - src/litestar_asyncapi/decorators.py
tests:
  - src/tests/unit/test_decorators.py
  - src/tests/unit/test_generator_components.py
plan_revision: 2
plan_commit: 36294c1
state_revision: 2
claimed_by: null
claimed_at: null
blocked_reason: null
unblock_condition: null
next_step: null
last_verified_at: 2026-11-05T03:20:00Z
last_verified_commit: cd01faa
verification_evidence: "RED: 6 new tests failed (ReplyDefinition missing, names not resolved, bare str accepted). GREEN: focused files green. make lint 0, make type-check 0, make test 0 (314 passed, 97.04%), make validate-asyncapi 0 (24 documents), make docs 0"
created_at: 2026-11-05T00:00:00Z
updated_at: 2026-11-05T03:20:00Z
commit: cd01faa
tags: [feature, contracts, ergonomics, tdd]
---

# Name-based security, server and reply references

## Objective

`OperationDefinition.security` and `ChannelDefinition.servers` accept lists of names, a bare `str` is rejected, and the new `ReplyDefinition(channel, messages, address)` resolves names after operations are populated; unknown names raise listing the valid names and a reply message must belong to the reply channel (R5).

## Context

- **Why `behavior_tdd`.** New accepted inputs and errors on public contract types.
- **Invariants.** Every generated `$ref` token passes through `_json_pointer_escape`. Reply messages resolve against the final message keys of the reply channel. Existing object and `Reference` forms keep working. No `correlation_id` string shorthand.
- **Canonical tests.** `src/tests/unit/test_generator_components.py` through `AsyncAPIGenerator.build_schema`; decorator acceptance in `src/tests/unit/test_decorators.py`.

## Steps

1. Write failing tests (RED): security and server names resolve; unknown names list valid names; bare `str` rejected; `ReplyDefinition` with address; cross-channel reply message error; unknown reply channel.
2. Implement (GREEN) `datastructures.py::ReplyDefinition` and validation, resolution in `generator.py::_populate_channels`, `_populate_operations` and a reply pass, decorator typing.
3. Refactor and run gates.

## Verification

- **Initial:** `uv run pytest src/tests/unit/test_generator_components.py -q --no-cov` fails (`ReplyDefinition` missing).
- **Final:** `make lint`, `make type-check`, `make test`, `make validate-asyncapi`, `make docs` exit `0`.

## Acceptance Criteria

- [x] R5: names for security, servers and replies; bare `str` rejected; unknown names list valid names; reply message membership enforced; object and `Reference` forms unchanged.

## Notes & Discoveries

- [2026-11-05 02:55] `_resolve_names` serves servers, security and reply messages; reply resolution runs after the operation loop against `Channel.messages` keys, so reply messages resolve to final (possibly suffixed) keys. `ReplyDefinition.channel` is required; a reply without a channel still uses `Reply`.
- [2026-11-05 03:05] Bare-`str` rejection raises `TypeError` from `__post_init__` (`ReplyDefinition.messages` too). `asyncapi_operation` validates `security` eagerly like `action`.
- [2026-11-05 03:10] `ReplyDefinition` is exported from `litestar_asyncapi` and listed on the Contracts reference page.
