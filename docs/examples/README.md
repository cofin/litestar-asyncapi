# Runnable examples

From the repository root, install the development dependencies with `make install`, then run an application through Litestar's CLI:

```bash
uv run litestar --app docs.examples.websocket_listener.app:app run
```

Replace the module with one listed in the [example guide](index.rst). Executing an `app.py` script alone constructs the application and exits; it does not start a server. PEP 723 metadata is provided for dependency-aware tools and points to this checkout.

The listener, stream, raw decorator, Channels, and error examples share `/asyncapi` and the optional `/asyncapi/playground` console. The HTMX example retains its distinct HTML-fragment UI at `/` and loads HTMX/Pico assets from external CDNs. Broker contracts do not implement a broker transport. All socket authorization and validation remain application responsibilities.
