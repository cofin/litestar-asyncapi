# litestar-asyncapi

AsyncAPI support for Litestar applications. This plugin generates AsyncAPI 3.0 documents for WebSocket routes and (best-effort) ChannelsPlugin channels, and provides JSON/YAML/UI renderers.

## Usage

```python
from litestar import Litestar
from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin

config = AsyncAPIConfig(
    use_handler_docstrings=True,
    create_examples=True,
    random_seed=1,
)

app = Litestar(plugins=[AsyncAPIPlugin(config=config)])
```

By default, the plugin serves docs at `/asyncapi/` with JSON at `/asyncapi/asyncapi.json` and YAML at `/asyncapi/asyncapi.yaml`.

When enabled, docstrings and handler metadata (summary, description, operation_id) are used to enrich AsyncAPI operations, and example payloads are generated for message schemas. AsyncAPI decorators still take precedence over inferred metadata.

## Documentation

Build the docs locally:

```bash
make docs
```

Link check:

```bash
make docs-linkcheck
```

The HTML output is written to `docs/_build/html`. The GitHub Pages deployment is handled by the docs workflow.

## CI and Release

- CI runs linting, type checks, and test matrix across supported Python versions.
- The release workflow is `publish.yml` (workflow name: `pypi`) and publishes to PyPI on GitHub release.

## Notes

- Operation IDs are generated deterministically and are unique across the document.
- Channel message references are emitted under each channel, with operations referencing those messages.
- Component key overrides are sanitized to valid schema component names.
- Channel parameter schemas are filtered to AsyncAPI v3-compatible fields.
