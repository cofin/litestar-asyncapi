# Plugin and configuration

```python
from litestar_asyncapi import AsyncAPIConfig, AsyncAPIPlugin, DocsConfig
```

Register one `AsyncAPIPlugin` per application. `AsyncAPIConfig` holds the document metadata, explicit contracts and discovery switches, and `DocsConfig` holds the documentation routes. The contract types that `AsyncAPIConfig.channels` accepts are on the [Contracts](contracts.md) page.

## Plugin

::: litestar_asyncapi.AsyncAPIPlugin
    options:
      members:
        - config
        - get_asyncapi
        - get_asyncapi_schema
        - get_asyncapi_json
        - clear_cache
        - create_docs_router

## Configuration

::: litestar_asyncapi.AsyncAPIConfig
    options:
      members:
        - title
        - version
        - description
        - spec_version
        - default_content_type
        - use_handler_docstrings
        - create_examples
        - strict_uniqueness
        - include_websocket_routes
        - include_raw_websocket_routes
        - include_sse_routes
        - include_channels_plugin
        - include_channels_plugin_topics
        - channel_payloads
        - channels
        - servers
        - components
        - operation_traits
        - message_traits
        - use_cache
        - docs

::: litestar_asyncapi.DocsConfig
