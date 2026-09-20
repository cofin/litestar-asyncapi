Runnable examples
=================

Run these commands from the repository root after ``make install``. Each module
contains PEP 723 dependency metadata, but executing the Python file alone does
not launch a server. The native Litestar CLI starts the application.

The listener, stream, decorator, Channels and error examples expose the shared optional console;
validation there is advisory, and Send can transmit invalid entered text. Open
``/asyncapi`` for documentation and connect only to a server you intend to use.

.. _websocket-listener:

WebSocket listener
------------------

Typed dataclass input and output. The application receives input and sends its returned value.

.. code-block:: bash

   uv run litestar --app docs.examples.websocket_listener.app:app run

.. literalinclude:: websocket_listener/app.py
   :language: python

.. _websocket-stream:

WebSocket stream
----------------

An asynchronous generator emits JSON object events until disconnected.

.. code-block:: bash

   uv run litestar --app docs.examples.websocket_stream.app:app run

.. literalinclude:: websocket_stream/app.py
   :language: python

.. _decorator-overrides:

Raw socket and multiple messages
--------------------------------

A raw socket accepts two named message types and returns a JSON result. Explicit metadata supplies its contract.

.. code-block:: bash

   uv run litestar --app docs.examples.decorator_overrides.app:app run

.. literalinclude:: decorator_overrides/app.py
   :language: python

.. _channels-plugin:

Channels and publish endpoint
-----------------------------

Actual generated news/alerts subscriber routes plus a POST publish endpoint. Internal subscriptions alone do not become documented routes.

.. code-block:: bash

   uv run litestar --app docs.examples.channels_plugin.app:app run

.. literalinclude:: channels_plugin/app.py
   :language: python

.. _htmx-websocket:

HTMX HTML fragments
-------------------

A distinct HTML-fragment UI at / uses HTMX with external CDN assets. Its text/HTML wire format is documented but unsupported by the JSON console.

.. code-block:: bash

   uv run litestar --app docs.examples.htmx_websocket.app:app run

.. literalinclude:: htmx_websocket/app.py
   :language: python

.. _error-handling:

Application error responses
---------------------------

An application returns structured responses for its handled validation cases. The intentional raise action remains an uncaught server error; documentation does not install exception handling.

.. code-block:: bash

   uv run litestar --app docs.examples.error_handling.app:app run

.. literalinclude:: error_handling/app.py
   :language: python

.. _broker-contracts:

Broker traits, security and replies
-----------------------------------

Explicit broker contracts without a transport implementation. Docs routes are disabled; use the headless export command.

.. code-block:: bash

   uv run litestar --app docs.examples.contracts:app run

.. literalinclude:: contracts.py
   :language: python

.. _native-schema:

Native schema plugin
--------------------

A native Litestar plugin and encoder define a custom Ticket value even with OpenAPI disabled.

.. code-block:: bash

   uv run litestar --app docs.examples.native_schema:app run

.. literalinclude:: native_schema.py
   :language: python

.. _mounted-docs:

Mounted and guarded docs
------------------------

Native Router nesting mounts /service/asyncapi. Send Authorization: demo-token to access UI, assets and schema; replace the demonstration guard in production.

.. code-block:: bash

   uv run litestar --app docs.examples.mounted_docs:app run

.. literalinclude:: mounted_docs.py
   :language: python

.. _custom-renderers:

Custom renderers
----------------

Scalar at /events, native JSON/YAML downloads, and a separate opt-in React console.

.. code-block:: bash

   uv run litestar --app docs.examples.renderers:app run

.. literalinclude:: renderers.py
   :language: python

Headless export
---------------

The broker example intentionally disables docs routes and still supports export:

.. code-block:: bash

   uv run litestar --app docs.examples.contracts:app asyncapi export --format json
   uv run litestar --app docs.examples.contracts:app asyncapi export --format yaml --output /tmp/contracts.yaml

Existing output files require ``--overwrite``. See :doc:`../usage/security-and-servers`
for server resolution, security declarations and the native ASGI mount limitation.
