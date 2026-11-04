---
type: Guide
title: "Architecture 01: System Overview and Plugin Lifecycle"
description: Native plugin initialization, isolated named docs routes, CLI registration and per-app document caches.
tags: [architecture, plugin, lifecycle, litestar]
status: stable
generated:
  by: flow-setup
  at: 2026-11-04
verified:
  - by: flow-completion
    at: 2026-11-04
    commit: dcc21c01b0e1e0bad5f4547dad61f075364629c2
sources:
  - id: core
    resource: src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin
    title: Plugin lifecycle, routes and cache
  - id: cli
    resource: src/litestar_asyncapi/cli.py::register_commands
    title: Headless export command
---

# System overview

AsyncAPIPlugin lives in plugins/core.py and is exported at the package root and plugins namespace. It implements native initialization and CLI hooks.

## Initialization and routes

on_app_init installs create_docs_router[^core] only when config.docs.enabled is true. DocsConfig owns path, guards, dependencies and renderers. The native Router disables OpenAPI inclusion and inherited DTOs, then registers native static assets and named render routes.

Default paths beneath /asyncapi are / for React documentation and /asyncapi.json for canonical JSON. DocsConfig.yaml enables /asyncapi.yaml and /asyncapi.yml; DocsConfig.interactive enables the shared React /playground console. The /assets route serves packaged resources. Supplied native renderers retain their own paths/media types; route names and paths must be unique. Unknown documentation paths return 404.

Named URL reversal handles native Router prefixes and correctly accumulated ASGI root_path. Litestar 2.24 arbitrary ASGI mounting does not accumulate the stripped prefix; this limitation is documented instead of replaced with another resolver.

on_cli_init registers asyncapi export through Litestar's CLI group, inheriting its app loader.[^cli] Headless export works with docs routes disabled.

## Cache ownership

Each plugin instance binds to one application and rejects reuse, even with caching disabled or after clear_cache. A private canonical document, normalized dictionary and immutable JSON bytes are populated lazily. get_asyncapi and get_asyncapi_schema return defensive copies; get_asyncapi_json returns immutable bytes. clear_cache clears all generated values while retaining ownership. use_cache=False regenerates without storing them.

Application encoders feed one normalization path shared by downloads, CLI, examples and UI. Schema generation uses a fresh native registry independent of OpenAPI state. Explicit server definitions prevent request Host from contaminating cached contracts.

## Startup ownership

An application accepts exactly one AsyncAPIPlugin, independently of the per-instance one-app cache binding. on_app_init rejects another instance even when docs are disabled. DocsConfig rejects every path normalizing to the application root because its fallback would claim unmatched requests. Browser fixtures must use a non-root docs router inside each mount.[^core]

[^core]: `src/litestar_asyncapi/plugins/core.py::AsyncAPIPlugin`
[^cli]: `src/litestar_asyncapi/cli.py::register_commands`
