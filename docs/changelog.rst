=========
Changelog
=========

All notable changes to this project will be documented in this file.

Unreleased
==========

Fixed
-----

* Kafka binding keys now use their official names: ``schemaRegistryUrl`` and
  ``schemaRegistryVendor`` on servers, and ``schemaIdLocation``,
  ``schemaIdPayloadEncoding`` and ``schemaLookupStrategy`` on messages.
  Documents using these bindings now pass official validation. This is a
  breaking change for anyone matching the old ``registry_*``, ``id_*`` or
  ``lookup_strategy`` keys.
* An explicit ``Schema(prefix_items=...)`` now exports Draft07 tuple items: the
  positional schemas become an ``items`` array and ``items`` becomes
  ``additionalItems``. Previously the Draft07 document carried ``prefixItems``,
  which validators ignore. Setting ``items``, ``additional_items`` and
  ``prefix_items`` together now raises ``ValueError``.
* A variable-length tuple with length limits, such as
  ``Annotated[tuple[int, ...], Parameter(max_items=3)]``, now keeps its item
  type. Previously its items were exported as ``oneOf`` an integer or anything.
* Length limits of zero (``min_items``, ``max_items``, ``min_length``,
  ``max_length``) are no longer dropped from payload schemas.
* An optional payload such as ``Payload | None`` now uses the examples declared
  on ``Payload`` instead of a randomly generated one.
* A payload given as a type name resolved through the application's
  ``signature_namespace`` now gets a generated example. Previously the example
  was omitted with an "Unsupported type" warning.
* A ``None`` default on an optional field such as ``int | None = None`` is now
  exported only on the field itself. Its non-null members, including shared
  enum components, no longer carry a contradictory ``default: null``.

0.2.0
=====

This release redesigns the plugin around native Litestar components and packaged upstream rendering. See :doc:`migration` for imports, configuration mappings and wire changes.

* Default to AsyncAPI 3.1, retain explicit 3.0, and correct Draft07 tuple output,
  examples, security references, null preservation and operation map keys.
* Reuse native Litestar schema generation, DTOs, encoders, routing, CLI and
  JSON/YAML render plugins. Remove the duplicate schema engine and unused shims.
* Discover finalized routes, preserve application-relative directions, and add
  typed explicit contracts with multiple messages, traits, replies and provenance.
* Bind cached documents to one application and return defensive public copies.
* Package AsyncAPI React component 3.2.1 with React 18.3.1 and optional Scalar
  1.69.2. Scalar remains opt-in due to demonstrated schema-display gaps.
* Replace the bespoke playground with optional upstream asyncapi-ws-plugin 0.1.0
  interaction. Validation is advisory; intentionally invalid input can be sent.
* Relocate UI sources and frontend tests to ``tools/frontend/``, keeping the repository root clean.
* Isolate Playwright output artifacts into ``.tmp/test-results``.
* Uncap the Litestar version constraint to ``litestar>=2.24.0`` without a major-version ceiling.
* Add headless JSON/YAML export and installed-wheel validation across Python
  3.10–3.14 with Litestar 2.24 as the supported minimum.

0.1.0
=====

- Initial release with AsyncAPI support for Litestar applications.
