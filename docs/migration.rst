Clean-break migration
=====================

This redesign makes intentional API breaks without a deprecation layer. Upgrade
Litestar to ``>=2.24,<3`` and test the generated document and your actual wire
messages. Python 3.10–3.14 is supported.

Configuration and imports
-------------------------

* Import ``AsyncAPIPlugin`` from ``litestar_asyncapi`` or
  ``litestar_asyncapi.plugins``. The singular ``litestar_asyncapi.plugin`` module
  is removed; the consolidated ``plugins`` package exports application and render
  plugins.
* Move flat documentation settings
  into ``AsyncAPIConfig(docs=DocsConfig(...))``. Select ``renderer="asyncapi"``
  (default) or ``"scalar"`` inside ``DocsConfig``.
* YAML routes now require ``DocsConfig(yaml=True)``. There is no separate YAML
  extra: current Litestar requires PyYAML even when the route is disabled.
* ``JsonRenderPlugin`` and ``YamlRenderPlugin`` are native Litestar classes.
  ``JSONRenderPlugin``, ``YAMLRenderPlugin`` and ``PlaygroundRenderPlugin`` were
  incorrect documentation names; use the actual mixed-case native names.
  Native defaults are OpenAPI paths/media types. Use ``DocsConfig`` defaults or
  configure AsyncAPI paths and vendor MIME types explicitly.
* ``AsyncAPIPlaygroundRenderPlugin`` and its bespoke JavaScript are removed.
  Enable ``DocsConfig(interactive=True)`` for the shared upstream React console.
  The redundant ``console`` flag is removed. Validation is advisory and invalid
  input may be deliberately sent; runtime validation belongs in your application.
* Old CDN script/style renderer options are removed. Browser assets are packaged
  and versioned with the wheel. Scalar is opt-in because of its documented tuple,
  zero-length and boolean-schema display gaps.
* Remove ``random_seed`` and custom ``create_examples`` factory objects/mappings.
  ``create_examples`` is a boolean; explicit examples provide reproducibility.
* Remove imports from ``litestar_asyncapi.typing`` and ``._typing``. Deleted exports
  are ``ATTRS_INSTALLED``, ``MSGSPEC_INSTALLED``, ``PYDANTIC_INSTALLED``, ``BaseModel``,
  ``Struct``, ``attrs_fields``, ``attrs_has`` and ``attrs_nothing``. Import real model
  types from their libraries and use native Litestar plugins.
* The empty ``litestar_asyncapi.extensions`` namespace and ``spec.base.UnsetType``
  are removed. ``spec.base.UNSET`` remains and is now native ``litestar.types.Empty``.
  Explicit null and omitted fields remain distinct.
* Custom AsyncAPI schema plugins, the duplicate registry and helper modules are
  removed. Register a native Litestar ``OpenAPISchemaPlugin`` on the application;
  see :doc:`usage/schema-generation`. No fallback duplicate type engine remains.

The direct configuration moves are:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Previous configuration
     - New configuration
   * - ``AsyncAPIConfig(path="/events")``
     - ``AsyncAPIConfig(docs=DocsConfig(path="/events"))``
   * - ``AsyncAPIConfig(enable_routes=False)``
     - ``AsyncAPIConfig(docs=DocsConfig(enabled=False))``
   * - ``AsyncAPIConfig(render_plugins=[...])``
     - ``AsyncAPIConfig(docs=DocsConfig(render_plugins=[...]))``

Documentation guards and dependencies are configured on ``DocsConfig``. The old
column describes removed APIs and is not executable with the new release.
Top-level ``message_traits`` and ``operation_traits`` mappings remain supported
on ``AsyncAPIConfig``. ``Components`` is an optional unified declaration for
traits and other reusable components.

Document and discovery changes
------------------------------

* AsyncAPI **3.1.0 is the default**; select ``spec_version="3.0.0"`` explicitly
  when needed. The root no longer assumes ``defaultContentType: application/json``
  for uncertain wire formats. Known inferred messages carry their own content type.
* Operation direction is application-relative: input is ``receive``, output is
  ``send``. Earlier client-relative documentation was incorrect. Generated Channels
  sockets are send-only; their receive loop does not process incoming payloads.
* ``operation_id`` remains decorator/definition metadata but becomes an
  ``operations`` map key. There is no ``operationId`` wire field or spec-model
  constructor argument. IDs remain case-insensitively unique.
* Use ``MessageDefinition``, ``OperationDefinition`` and ``ChannelDefinition`` for
  explicit contracts. Multiple named messages per operation are supported. Channel
  key and destination address are separate; operations reference their selected
  channel's messages. Conflicts now fail with deterministic provenance diagnostics.
* Fixed tuples export Draft07 ``items: [schema, ...]`` and length bounds, replacing
  the incorrect ``prefixItems`` wire representation. Variadic tuples remain
  unbounded. Unsupported modern semantics fail explicitly; explicit
  ``MultiFormatSchema`` remains available.
* Message examples are wire ``MessageExample`` objects (``{"payload": ...}``), not
  arbitrary bare entries. Decorator example values are wrapped for you. An explicit
  empty list suppresses fallback generation, and explicit null is preserved.
* Operation/server security entries are schemes or references, not OpenAPI
  requirement-name maps. Put named definitions in ``Components.security_schemes``.
* Only finalized native routes are inferred. Internal Channels subscriptions no
  longer create phantom endpoints. Declare external broker channels explicitly.
  Raw sockets require explicit metadata, or opt into uncertain discovery with
  ``include_raw_websocket_routes=True``. SSE inference is unsupported.
* A plugin instance belongs to one app, including with caching disabled. Public
  mutable accessors return defensive copies. ``clear_cache()`` preserves ownership.

Before deploying, inspect JSON output and test real application encoders, DTOs,
security and message validation. Documentation guards and security declarations
are separate from socket authorization. See :doc:`usage/renderers` for the precise
interactive capability boundary and :doc:`examples/index` for executable examples.
