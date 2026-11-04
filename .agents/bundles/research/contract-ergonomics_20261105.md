---
type: Research
research_id: "contract-ergonomics-20261105"
title: "Proposal: OpenAPI Inheritance and Name-Based References for Explicit Contracts"
description: "Proposal to inherit document metadata, security schemes and servers from Litestar's OpenAPI config, accept names instead of JSON-pointer references, and rewrite the explicit-contract example. Under review."
scope: architecture
status: draft
state: open
promoted_to: null
tags: [research, proposal, openapi, ergonomics, contracts]
generated:
  by: flow/0.26.0
  at: 2026-11-05T00:00:00Z
sources:
  - id: example
    resource: docs/examples/contracts.py
    title: Current explicit-contract example
  - id: config
    resource: src/litestar_asyncapi/config.py::AsyncAPIConfig
    title: Plugin configuration
  - id: defs
    resource: src/litestar_asyncapi/asyncapi/datastructures.py::OperationDefinition
    title: Explicit contract definitions
  - id: litestar-security
    resource: litestar/security/base.py::AbstractSecurityConfig.on_app_init
    title: Litestar auth backends add OpenAPI components and security requirements at startup
---

# Proposal: OpenAPI Inheritance and Name-Based References

## Problem

`docs/examples/contracts.py` is hard to read, for two reasons.

- **It uses every advanced feature once.** Servers, security, operation and message traits, a correlation ID and a reply all appear in a single config. Traits in particular exist to share behavior across operations, but here each one is used exactly once.
- **The API exposes AsyncAPI JSON pointers.** Users write `Reference("#/components/securitySchemes/credentials")`, `Reply(channel=Reference("#/channels/results"), messages=[Reference("#/channels/results/messages/Result")])` and `CorrelationId(location=...)`.

The plugin also ignores `app.openapi_config`. It reuses only the schema plugins from it.

## Facts

- `litestar.openapi.OpenAPIConfig` holds:
  - document metadata: `title`, `version`, `description`, `summary`, `contact`, `license`, `terms_of_service`, `tags`, `external_docs`;
  - security: `components` (including `security_schemes`) and `security` (requirements);
  - `servers`, where the default is `[Server(url="/")]`.
- Litestar auth backends (`AbstractSecurityConfig.on_app_init`, used by JWTAuth, SessionAuth and others) append their `openapi_components` and `security_requirement` to `app_config.openapi_config` at startup.
- HTTP handlers have `security` and `resolve_security()`. WebSocket handlers have no `security` parameter.
- `AsyncAPIConfig` has `title="AsyncAPI"`, `version="1.0.0"` and `description`, but no contact, license, terms of service, tags or external docs. `OperationDefinition.security` accepts `SecurityScheme | Reference`. `reply` accepts `Reply | Reference`. Traits already accept string names.
- The payload of an explicit `MessageDefinition` already accepts Python types, which go through the native schema creator.

## Proposal

### 1. Inherit from OpenAPI by default

- **Document metadata.** `AsyncAPIConfig` metadata fields default to unset. An unset field is filled from `app.openapi_config`, and an explicit value wins. The fields are `title`, `version`, `description`, and new fields `contact`, `license`, `terms_of_service`, `tags` and `external_docs`.
- **Security schemes.** OpenAPI security schemes map to AsyncAPI security schemes:
  - `http` + `bearer` → `http`
  - `apiKey` (header or query) → `httpApiKey`
  - `oauth2` → `oauth2`, with `scopes` renamed to `availableScopes`
  - `openIdConnect` → `openIdConnect`

  Global OpenAPI `security` requirements apply to the derived WebSocket servers.
- **Servers.** Servers are derived from OpenAPI servers whose URLs are absolute: `https://h/v1` → host `h`, protocol `wss`, pathname `/v1`. Relative URLs, including Litestar's default `/`, are skipped.
- **Off switch.** `inherit_openapi: bool = True` disables all of the above.
- **Breaking change.** The default title becomes the OpenAPI title ("Litestar API" by default) instead of "AsyncAPI".

### 2. Name-based references

| Field | Accepts | Refers to |
| --- | --- | --- |
| `OperationDefinition.security` | `str` | a scheme name, inherited or configured |
| New `ReplyDefinition(channel="results", messages=["Result"])` | names | a channel and its messages |
| `MessageDefinition.correlation_id` | `str` | a runtime expression |
| `ChannelDefinition.servers` | `str` | a server name |

Names resolve when the document is built. An unknown name raises an error that lists the valid names. The existing object and `Reference` forms keep working.

### 3. Rewrite and split the example

- **Learn page.** A simple, typed broker request/reply using dataclass payloads and `ReplyDefinition` by name.
- **Security-and-servers page.** An app using `JWTAuth` whose scheme is inherited, `security=["BearerToken"]`, one trait shared by two operations, and a correlation ID.

## Open Questions for Review

- Is inheriting by default correct, or does it surprise users whose AsyncAPI document describes something other than the HTTP API? Is the OpenAPI-to-AsyncAPI security mapping lossless?
- Is deriving `wss` servers from HTTP servers sound when WebSocket routes may live on another host?
- Does name resolution conflict with names users already use? For example, a channel key that is also a component channel name.
- Does any of this break litestar-vite's consumer, which reads `servers`, `operations`, `reply` and the document title?

## Review Outcome and Revised Proposal

Two reviews ran: a design review against the code and the official schemas, and a review of the downstream litestar-vite consumer. The verdict is to do it, with the changes below.

### Revisions

- **Metadata.** `title`, `version`, `description`, `contact`, `license`, `terms_of_service` and `external_docs` are inherited from `app.openapi_config` when unset. Config fields are typed `str | None = None` (or the matching optional type), and the effective value is resolved in the generator.
  - Tags are not inherited, because OpenAPI tags group HTTP routes.
  - `License.identifier` and `summary` have no AsyncAPI Info equivalent, which is documented.
- **Security schemes.** Scheme definitions are inherited into `components.securitySchemes`, so `security=["BearerToken"]` works. Requirements are not inherited: OpenAPI's AND and "optional auth" semantics, plus auth `exclude` routes, cannot be expressed in AsyncAPI. One adapter does the conversion:
  - `http` + bearer → `http` with `scheme: "bearer"` (lowercased), dropping `name`. JWTAuth emits `"Bearer"` plus `name`, which fails `BearerHTTPSecurityScheme`.
  - Other `http` schemes, for example `basic`, map to `http`.
  - `apiKey` in a header, query or cookie → `httpApiKey`.
  - `oauth2` → `oauth2`, with `availableScopes` always present (`{}` when no scopes are set). A flow with a relative token or authorization URL is skipped with a warning.
  - `openIdConnect` maps as-is. `mutualTLS` → `X509`.
  - Any type that cannot be mapped is skipped with a warning.
  - Each mapped type is validated through `make validate-asyncapi` for 3.0 and 3.1.
- **Servers.** Servers are opt-in (`inherit_openapi_servers=False` by default) because channels with no `servers` belong to every server.
  - When enabled, only absolute OpenAPI URLs are used: `http` → `ws`, `https` → `wss`, with server variables and description carried over.
  - Derived servers are bound only to WebSocket-sourced channels. A host is never invented.
- **Reading OpenAPI.** `app.openapi_config` is read lazily in `build_asyncapi`, after the auth hooks have run.
  - `openapi_config=None` is handled.
  - `components` may be a list. The adapter merges it without mutating the config, and never calls `to_openapi_schema()` or `app.openapi_schema`.
  - A name collision with a different configured scheme raises, naming both sources.
- **Name-based references.**
  - `security` and `servers` accept lists of names. A bare `str` passed in place of a list is rejected.
  - `ReplyDefinition(channel, messages, address)` is resolved in a pass after `_populate_operations` through the final message keys. The pass raises on an unknown channel or message and lists the valid names. A message must belong to the reply channel.
  - The field is typed `ReplyDefinition | Reply | Reference`.
  - The `correlation_id: str` shorthand is dropped, because a plain `str` means a component name everywhere else.
- **Example.**
  - The Learn page shows a typed broker request/reply. Its reply channel declares its own `send` operation, so clients can type it. Without one, litestar-vite guesses the direction.
  - The advanced example uses JWTAuth with its inherited scheme.
  - Payload `$ref`s stay under `#/components/schemas`, because litestar-vite throws on any other `$ref`.

### litestar-vite findings

- **The proposal is neutral to slightly positive for litestar-vite.** Its TypeScript ignores `info`, `servers`, `security`, `reply` and operation ids.
- **This branch:**
  - Explicit bindings end the path guessing.
  - Send-only listeners are now classified correctly.
  - ChannelsPlugin routes at `/ws*` change from `websocket` to `channels`.
  - SSE and topic channels now appear.
  - The operation renames and the Kafka keys don't affect it.
- **Python 3.11 floor.** litestar-vite supports 3.10 and pins `litestar-asyncapi>=0.2.0`, so its universal lock stays on 0.2.0 until it raises its own floor or adds markers.
- **Issues inside litestar-vite, not this repo:**
  - `reply.*.$ref` is not rewritten after it re-keys channels.
  - The runtime opens a WebSocket for SSE channels.
  - Client URLs are built from the channel key rather than `address`.
  - It could prefer `x-litestar-source` over bindings.
- **Shared types.** If AsyncAPI component schema names match the names Litestar's OpenAPI gives the same Python types, litestar-vite could share types from its OpenAPI client instead of duplicating them. This is worth pinning with a test.
