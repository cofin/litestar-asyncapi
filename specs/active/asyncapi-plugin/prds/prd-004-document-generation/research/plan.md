# Research Notes: PRD-004 Document Generation

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17

---

## 1. Orchestration lessons from Litestar OpenAPI

Litestar’s OpenAPI implementation is a useful blueprint because it:

- constructs a spec object model (OpenAPI spec dataclasses)
- uses a separate “internal” package (`litestar/_openapi`) for generation logic
- caches both the spec object and its serialized dict representation
- builds a dedicated router for docs endpoints

For AsyncAPI, we want the same separation:
- `litestar_asyncapi/spec/*` for object model
- `litestar_asyncapi/_asyncapi/*` for generation/discovery internals
- `litestar_asyncapi/plugins.py` for render plugins (PRD-005)

---

## 2. Document build responsibilities

PRD-004 should consolidate the pieces from prior phases:

1. Read config:
   - title/version/description
   - default content type
   - server definitions
   - feature flags (discovery toggles)
2. Invoke extractors (PRD-003):
   - websocket channels
   - ChannelsPlugin channels (optional)
3. Invoke schema generator (PRD-002):
   - for message payload types
   - for channel parameters (if modeled)
4. Populate spec root (PRD-001 objects):
   - `channels`
   - `operations`
   - `components.schemas`

This phase should avoid mixing UI concerns or request/response concerns; it should return pure spec objects and
serializable dicts.

---

## 3. Caching and invalidation decisions

### Option A: Lazy caching only (simplest)

- Build document on first request, cache.
- Provide explicit invalidation (e.g. on startup completion, or via config method).

Pros: simplest and robust.
Cons: if routes change at runtime (dynamic route registration), cached doc becomes stale.

### Option B: ReceiveRoutePlugin invalidation (closer to OpenAPI)

- Implement route-receive hooks and invalidate cache when new websocket routes are registered.

Pros: stays accurate for dynamic apps.
Cons: extra complexity in plugin class and interactions with Litestar’s route lifecycle.

Recommendation:
- Start with Option A for initial delivery.
- Add Option B as a targeted improvement once the core works and tests exist.
