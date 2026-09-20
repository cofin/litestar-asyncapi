Getting started
===============

Install with ``uv add litestar-asyncapi``. Supported runtimes are Python 3.10–3.14
and Litestar ``>=2.24,<3``. Node is needed only to rebuild browser assets.

The listener example is a complete application:

.. literalinclude:: examples/websocket_listener/app.py
   :language: python

From this repository, start it with:

.. code-block:: bash

   uv run litestar --app docs.examples.websocket_listener.app:app run

Open ``/asyncapi/``. Default JSON is at ``/asyncapi/asyncapi.json`` with
``application/vnd.asyncapi+json``. ``DocsConfig(yaml=True)`` adds YAML at
``/asyncapi/asyncapi.yaml`` and ``/asyncapi/asyncapi.yml`` with
``application/vnd.asyncapi+yaml``. YAML routes are disabled by default, although
Litestar itself requires PyYAML.

The document defaults to AsyncAPI 3.1. Set ``spec_version="3.0.0"`` for 3.0.
The example explicitly enables interaction; ordinary ``DocsConfig()`` does not.
See :doc:`usage/renderers` for its advisory validation and wire-format limits.

See :doc:`migration` before upgrading an existing application.
