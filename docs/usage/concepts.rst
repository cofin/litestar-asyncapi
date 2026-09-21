Concepts and lifecycle
======================

AsyncAPI describes the application. A listener's incoming ``data`` is a
``receive`` operation; its returned value is a ``send`` operation. A stream
produces ``send`` operations. Client-facing console labels invert that viewpoint.

A channel's key identifies the document entry; its ``address`` is the actual
communication destination. ``OperationDefinition.operation_id`` becomes the
key in ``operations`` and is not emitted as an ``operationId`` field. Each
operation references messages belonging to its selected channel.

Finalized Litestar routes determine discovery. Native layered
``include_in_schema`` options apply. Compatible discoveries merge only when
route identity agrees; ambiguous definitions produce diagnostics with provenance.
Explicit configured channels replace inferred contracts at the same address.
Identifiers are stable and operation identity is case-insensitively unique.

Generation stays lazy until an accessor, HTTP request or CLI export asks for a
document. A fresh native Litestar schema registry and the app's schema plugins
supply model schemas. The adapter converts their supported JSON Schema constructs
to Draft07, and assembly resolves local AsyncAPI references without fetching
external resources. Literal ``$ref`` keys inside examples are data.

``AsyncAPIPlugin`` binds to one application even with ``use_cache=False``.
Create one instance per app. ``clear_cache()`` invalidates generated values but
retains that ownership. ``get_asyncapi()`` and ``get_asyncapi_schema()`` return
defensive copies; ``get_asyncapi_json()`` returns immutable cached bytes.
Application encoders normalize JSON, YAML and documentation from one canonical
representation. Request hostnames never become cached server declarations.
