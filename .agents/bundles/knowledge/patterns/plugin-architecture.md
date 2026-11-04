---
type: Pattern
title: Plugin Architecture Pattern
description: Native Litestar reuse, isolated documentation integration and cache ownership.
tags: [patterns, plugin, litestar, slots, dataclasses]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-setup
    at: 2026-11-04
    commit: 49bc3c8
sources:
  - id: core
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.create_docs_router
    title: Native docs router
  - id: init
    resource: src/litestar_asyncapi/plugins/__init__.py
    title: Renderer exports
  - id: slots
    resource: pyproject.toml::tool.slotscheck
    title: Narrow slotscheck exclusion
---

# Plugin Architecture Pattern

Use the native Litestar component whenever it supplies the behavior. Do not copy a renderer, serializer, router, static file server, schema registry, example factory or CLI loader merely to rename OpenAPI to AsyncAPI. Own only AsyncAPI semantics and the integration adaptation that native components cannot provide.

## Package and renderer ownership

The single plugins/ package contains core.py, renderers.py and public exports. Keep public exports stable at the package root and in `plugins/__init__.py`.

JsonRenderPlugin and YamlRenderPlugin are direct native exports.[^init] AsyncAPIRenderPlugin aliases OpenAPIRenderPlugin. DocsConfig configures AsyncAPI paths and vendor media types; directly constructing a native renderer retains its native defaults. Native rendering receives canonical normalized values and the real request with its resolved type encoders.

Do not add local YAML dependency detection or an extra that repeats Litestar's requirements. Litestar 2.24 imports and requires PyYAML. Renderer selection is optional; dependency absence is a separate claim that must be checked against installed metadata.

Do not place an upper ceiling constraint on Litestar in package dependencies. Maintain `litestar>=2.24.0` without an upper bound so downstream applications on future Litestar versions install without artificial resolution blocks.

## Cache ownership

One AsyncAPIPlugin instance binds to one app at first document access. Reject another app even when caching is disabled. clear_cache clears generated values but retains app ownership. Keep the canonical document, normalized schema and JSON bytes private; return defensive copies for mutable public accessors.

Use native Litestar serialization (`encode_json`, `decode_json`, `default_serializer`) directly. Do not maintain redundant serialization wrapper layers. Preserve explicit user null values. Do not let request Host or mutable caller dictionaries poison canonical output.

## Native lifecycle and routing

Use native plugin initialization and Router with include_in_schema=False[^core], dto=None and return_dto=None. Apply authorization through native layered guards and dependencies. Use native static serving and URL reversal when adding packaged documentation routes.

## Slots

Owned configuration and model classes remain slotted. Native OpenAPIRenderPlugin is unslotted; owned UI adapters inheriting it have a narrow documented slotscheck exclusion.[^slots] Do not duplicate the native base to satisfy an incompatible local layout rule. Run make lint and make slotscheck.

[^core]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin.create_docs_router`
[^init]: `src/litestar_asyncapi/plugins/__init__.py`
[^slots]: `pyproject.toml::tool.slotscheck`
