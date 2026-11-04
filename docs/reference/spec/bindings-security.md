# Bindings and security

```python
from litestar_asyncapi.spec import SecurityScheme, SecuritySchemeType
from litestar_asyncapi.spec.bindings import KafkaChannelBinding, WebSocketChannelBinding
```

Security schemes describe how clients authenticate; declaring one does not enforce it. Bindings add protocol-specific details to servers, channels, operations and messages. Use a binding model as a value in a `bindings` mapping keyed by protocol, such as `{"kafka": KafkaChannelBinding(partitions=3)}`.

## Security

::: litestar_asyncapi.spec.SecurityScheme

::: litestar_asyncapi.spec.SecuritySchemeType

## Bindings

::: litestar_asyncapi.spec.bindings.Binding

### WebSocket

::: litestar_asyncapi.spec.bindings.WebSocketServerBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.WebSocketChannelBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.WebSocketMessageBinding
    options:
      heading_level: 4

### Kafka

::: litestar_asyncapi.spec.bindings.KafkaServerBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.KafkaChannelBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.KafkaMessageBinding
    options:
      heading_level: 4

### AMQP

::: litestar_asyncapi.spec.bindings.AMQPServerBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.AMQPChannelBinding
    options:
      heading_level: 4

::: litestar_asyncapi.spec.bindings.AMQPMessageBinding
    options:
      heading_level: 4
