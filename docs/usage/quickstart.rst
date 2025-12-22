Quickstart
==========

Install the plugin:

.. code-block:: bash

   pip install litestar-asyncapi

Enable the plugin in your Litestar app:

.. code-block:: python

   from litestar import Litestar
   from litestar_asyncapi import AsyncAPIPlugin

   app = Litestar(plugins=[AsyncAPIPlugin()])

The documentation UI is served at ``/asyncapi/`` by default, with JSON and YAML available at
``/asyncapi/asyncapi.json`` and ``/asyncapi/asyncapi.yaml``.
