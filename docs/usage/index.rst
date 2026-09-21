Usage guides
============

Use inferred listener and stream contracts where Litestar knows the payload
shape. Add explicit definitions for raw sockets, external brokers, or metadata
that cannot be inferred from runtime handlers.

.. toctree::
   :maxdepth: 1

   quickstart
   concepts
   websocket-handlers
   decorators
   schema-generation
   channels-plugin
   renderers
   security-and-servers
