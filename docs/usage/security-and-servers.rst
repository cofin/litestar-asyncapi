Security, servers and mounted docs
==================================

A ``Server`` separates ``protocol`` (``ws`` or ``wss``), ``host`` (including an
optional port), and ``pathname`` (deployment prefix). The channel ``address`` is
its destination beneath that prefix. For example, ``host="localhost:8000"``,
``pathname="/service"`` and ``address="/events"`` resolve to
``ws://localhost:8000/service/events``. Supply the prefix once. Request hosts do
not synthesize server declarations.

Security schemes belong in ``Components.security_schemes``. Servers and
operations reference them with ``Reference("#/components/securitySchemes/name")``.
Declarations document requirements; they do not install runtime authentication.
Query API keys use ``type="httpApiKey"`` with ``in_="query"``. Arbitrary headers
cannot be added by a browser WebSocket; no proxy is provided.

Explicit broker, traits and replies
-----------------------------------

This executable app describes a broker contract and supports headless export.
It intentionally creates no broker transport or subscription:

.. literalinclude:: ../examples/contracts.py
   :language: python

Reply messages must belong to their reply channel. Local references are checked
against allowed AsyncAPI locations; external references are preserved without
fetching. Explicit components cannot silently replace native generated schemas.

Guarded, mounted documentation
------------------------------

Native docs guards apply to UI, JSON, YAML, console and assets. These protect the
documentation routes, not the sockets described by the schema:

.. literalinclude:: ../examples/mounted_docs.py
   :language: python

The example's demonstration token is not a production authentication system.
Request ``/service/asyncapi/`` with ``Authorization: demo-token``. A native Router
prefix and a correctly supplied ASGI ``root_path`` are included by native URL
reversal. For example, ``root_path="/gateway"`` adds that external prefix to links.
Litestar 2.24's arbitrary ASGI mount does not itself accumulate that root path;
such an integration must provide the correct accumulated scope. The plugin does
not reconstruct URLs from ``raw_path`` or provide a second URL resolver.

Headless export
---------------

CLI app loading is Litestar's native mechanism. These commands work with the
contract example's disabled docs routes:

.. code-block:: bash

   uv run litestar --app docs.examples.contracts:app asyncapi export
   uv run litestar --app docs.examples.contracts:app asyncapi export --format yaml --output asyncapi.yaml

Output defaults to stdout. Existing files require ``--overwrite``; errors use
stderr and a nonzero exit. JSON/YAML exports use application encoders and explicit
configured servers. Use the upstream AsyncAPI CLI for conversion and code generation.
