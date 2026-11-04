# Generator and discovery

```python
from litestar_asyncapi.asyncapi.extractors import (
    extract_channels_plugin_channels,
    extract_sse_channels,
    extract_websocket_channels,
)
from litestar_asyncapi.asyncapi.generator import AsyncAPIGenerator
```

`AsyncAPIPlugin` runs the generator and caches its result, so applications rarely call it directly. Use the generator to build a document outside the plugin, and the extractors to inspect what discovery finds.

## Generator

::: litestar_asyncapi.asyncapi.generator.AsyncAPIGenerator

## Extractors

Each extractor returns the channels found by one discovery source. The generator merges them, applies explicit contracts and rejects conflicting keys.

::: litestar_asyncapi.asyncapi.extractors.extract_websocket_channels

::: litestar_asyncapi.asyncapi.extractors.extract_sse_channels

::: litestar_asyncapi.asyncapi.extractors.extract_channels_plugin_channels

## Discovered definitions

The extractors return definitions that add their source and provenance to the [contract types](contracts.md#definitions).

::: litestar_asyncapi.asyncapi.datastructures.DiscoveredChannel

::: litestar_asyncapi.asyncapi.datastructures.DiscoveredOperation
