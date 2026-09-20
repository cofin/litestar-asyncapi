==================
Security & Servers
==================

AsyncAPI 3.0 allows defining deployment servers, protocols, and security schemes that govern access to event channels.

Configuring Servers
===================

Servers represent target hosts where the application channels are available. Configure servers via ``AsyncAPIConfig.servers``:

.. code-block:: python

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.spec import Server

    config = AsyncAPIConfig(
        title="Production Gateway",
        servers={
            "production": Server(
                host="api.example.com",
                protocol="wss",
                pathname="/ws",
                description="Production secure WebSocket gateway",
            ),
            "staging": Server(
                host="staging-api.example.com",
                protocol="wss",
                pathname="/ws",
                description="Staging WebSocket environment",
            ),
        },
    )

Security Schemes
================

Security schemes describe authentication and authorization mechanisms required to connect to servers or channels.

Common schemes include:
- **API Key**: Query parameter, header, or cookie key.
- **HTTP**: Basic authentication or Bearer tokens (JWT).
- **OAuth 2.0**: Scoped authorization flows.

.. code-block:: python

    from litestar_asyncapi import AsyncAPIConfig
    from litestar_asyncapi.spec import SecurityScheme

    security_schemes = {
        "apiKeyAuth": SecurityScheme(
            type="apiKey",
            name="X-API-KEY",
            in_="header",
            description="API key passed via connection headers",
        ),
        "bearerAuth": SecurityScheme(
            type="http",
            scheme="bearer",
            bearer_format="JWT",
            description="JWT bearer token in authorization header",
        ),
    }

    config = AsyncAPIConfig(
        title="Secured WebSocket API",
        security_schemes=security_schemes,
    )
