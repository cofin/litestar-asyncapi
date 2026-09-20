Litestar AsyncAPI
=================

Generate AsyncAPI 3.1 documents from finalized Litestar WebSocket routes, or
supply explicit channel contracts. Serve packaged documentation with optional
WebSocket interaction, or export documents without mounting any docs routes.

The implementation reuses Litestar's schema creator, application encoders,
routers, CLI, and JSON/YAML renderers. Inline schemas use Draft07 tuple semantics.
AsyncAPI 3.0 remains an explicit configuration option.

Start with :doc:`getting-started`, then consult the :doc:`usage/index` and
:doc:`examples/index`. Existing users should read :doc:`migration` before upgrading.
The :doc:`usage/renderers` guide records Scalar display limitations and the
optional console's advisory validation behavior.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   getting-started
   usage/index
   examples/index
   migration
   reference/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   contribution-guide
   changelog
