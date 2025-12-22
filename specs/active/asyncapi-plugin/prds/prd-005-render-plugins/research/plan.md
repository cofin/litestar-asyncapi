# Research Notes: PRD-005 Render Plugins

**Parent Research**: `specs/active/asyncapi-plugin/research/plan.md`
**Created**: 2025-12-17

---

## 1. Why render plugins (vs hard-coded endpoints)

Litestar’s OpenAPI uses render plugins to decouple:
- how a schema is produced (generator)
- from how it is presented (json/yaml/ui)

This is a good fit for AsyncAPI because:
- some users will only want JSON/YAML download routes
- others will want an interactive UI
- some will want custom UIs or custom serialization constraints

So the plugin should treat rendering as pluggable and small.

---

## 2. JSON/YAML serialization specifics

### JSON

Use Litestar’s JSON encoder path so that:
- user type encoders registered on the app/router are respected
- output matches the framework’s JSON behavior elsewhere

### YAML

YAML should convert complex objects into builtins before dumping, so:
- any sentinel values or custom objects are converted properly
- output does not include Python-specific representations

Litestar’s OpenAPI YAML plugin uses `msgspec.to_builtins()` for this reason; we can mirror it.

---

## 3. UI implementation approach

The parent PRD recommends a CDN-delivered AsyncAPI UI using `@asyncapi/react-component` or similar.

Key considerations:
- The HTML template should embed the schema in a safe and deterministic way (avoid XSS in docs).
- Large schemas should not be duplicated unnecessarily (consider fetching JSON endpoint from the UI page instead of inline).
- The UI should be optional and disabled by default if users want minimal footprint.

Recommendation for initial version:
- Provide a minimal HTML template that fetches the JSON schema endpoint at runtime.
- This avoids embedding huge JSON blobs into HTML responses and reduces memory overhead.
