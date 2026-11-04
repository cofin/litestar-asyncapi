# Contracts

```python
from litestar_asyncapi import (
    ChannelDefinition,
    MessageDefinition,
    OperationDefinition,
    asyncapi_message,
    asyncapi_operation,
)
```

The decorators refine what discovery infers from a route handler. The definition types describe the same contracts explicitly: decorators take `MessageDefinition` values, and `AsyncAPIConfig.channels` takes `ChannelDefinition` values. Payload and header types stay Python types until the document is built.

## Decorators

::: litestar_asyncapi.asyncapi_operation

::: litestar_asyncapi.asyncapi_message

## Definitions

::: litestar_asyncapi.ChannelDefinition

::: litestar_asyncapi.OperationDefinition

::: litestar_asyncapi.MessageDefinition

## Transport markers

Every discovered channel carries an `x-litestar-source` extension that names the transport it came from. Channels declared in `AsyncAPIConfig.channels` carry none.

::: litestar_asyncapi.asyncapi.datastructures.SOURCE_EXTENSION

::: litestar_asyncapi.asyncapi.datastructures.SOURCE_MARKERS

::: litestar_asyncapi.asyncapi.datastructures.DiscoverySource
