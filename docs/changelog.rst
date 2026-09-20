=========
Changelog
=========

All notable changes to this project will be documented in this file.

Unreleased: native Litestar redesign
====================================

This release makes clean API breaks. See :doc:`migration` for imports,
configuration mappings and wire changes.

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
* Add headless JSON/YAML export and installed-wheel validation across Python
  3.10–3.14 with Litestar 2.24 as the supported minimum.

0.4.1
=====

- Modernize infrastructure and documentation to align with Litestar 2026 standards.
- Introduced AsyncAPI 3.0 specification models.
- Security hardening for interactive UIs.
- Hardening of operation ID generation.
- Expanded test coverage to 92%.
- Runtime versioning and improved project metadata.
