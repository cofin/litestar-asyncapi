# Schema generation

```python
from litestar_asyncapi.asyncapi.schema_generation import AsyncAPISchemaGenerator
from litestar_asyncapi.asyncapi.schema_generation.dialect import to_asyncapi_schema
```

Payload and header schemas come from Litestar's own schema generation, with a registry that belongs to one document build. The result is exported as JSON Schema Draft07, the default schema format of AsyncAPI 3.

## Schema generator

::: litestar_asyncapi.asyncapi.schema_generation.AsyncAPISchemaGenerator

## Draft07 export

::: litestar_asyncapi.asyncapi.schema_generation.dialect.to_asyncapi_schema
