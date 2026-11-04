# Specification models

```python
from litestar_asyncapi.spec import AsyncAPI, Channel, Message, Operation, Schema
```

The generator builds a document from these dataclasses, and `AsyncAPIConfig` accepts them for servers, components and traits. Each model serializes to the AsyncAPI wire format through `to_schema`, which camel-cases field names and leaves out fields that were never set.

- [Document](document.md): the root `AsyncAPI` object, info, servers, components and references.
- [Channels and operations](channels.md): channels, parameters, operations and replies.
- [Messages and schemas](messages.md): messages, traits, examples and payload schemas.
- [Bindings and security](bindings-security.md): security schemes and protocol bindings.
